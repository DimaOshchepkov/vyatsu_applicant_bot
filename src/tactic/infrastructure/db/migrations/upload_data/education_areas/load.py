import asyncio
import json
import os
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

from shared.models import (
    ContestType,
    EducationLevel,
    Program,
    ProgramContestExam,
    ProgramTimelineBinding,
    ScoreStat,
    StudyDuration,
    StudyForm,
    Subject,
    TimelineEvent,
    TimelineEventName,
    TimelineType,
)
from tactic.settings import db_settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "program_info_full.json")


async def get_or_create(db: AsyncSession, model, values: set[str], key_field="name"):
    result = await db.execute(select(model))
    existing = result.scalars().all()
    existing_map = {getattr(x, key_field): x for x in existing}

    new_objects = []
    for val in values:
        if val not in existing_map:
            obj = model(**{key_field: val})
            db.add(obj)
            new_objects.append(obj)

    if new_objects:
        await db.commit()
        for obj in new_objects:
            await db.refresh(obj)
            existing_map[getattr(obj, key_field)] = obj

    return {k: v.id for k, v in existing_map.items()}


async def load_reference_data(json_data: list[dict], db: AsyncSession):
    education_levels = {entry["level"] for entry in json_data}
    study_forms = {entry.get("Форма обучения:", "").strip() for entry in json_data}
    study_durations = {entry.get("Срок обучения:", "").strip() for entry in json_data}

    subjects, contest_types, timeline_type, timeline_name = set(), set(), set(), set()
    for entry in json_data:
        for contest, exams in entry.get("contest_exams", {}).items():
            contest_types.add(contest.strip())
            for subject in exams:
                subject_clean = subject.replace(" (на выбор)", "").strip()
                if subject_clean:
                    subjects.add(subject_clean)

        # Сбор типов таймлайна
        for t in ("budget_endpoints", "paid_endpoints"):
            if t in entry:
                timeline_type.add(t)

                # Сбор названий событий
                for event in entry[t]:
                    if isinstance(event, dict):
                        name = next(iter(event.keys()), None)
                        if name:
                            timeline_name.add(name.strip())

    timeline_type.add("budget_endpoints")
    timeline_type.add("paid_endpoints")

    return {
        "education_levels": await get_or_create(db, EducationLevel, education_levels),
        "study_forms": await get_or_create(db, StudyForm, study_forms),
        "study_durations": await get_or_create(
            db, StudyDuration, study_durations, key_field="years"
        ),
        "subjects": await get_or_create(db, Subject, subjects),
        "contest_types": await get_or_create(db, ContestType, contest_types),
        "timeline_type": await get_or_create(db, TimelineType, timeline_type),
        "timeline_name": await get_or_create(db, TimelineEventName, timeline_name),
    }


def create_program(entry: dict, ref_maps: dict) -> Program:
    return Program(
        title=entry["title"],
        url=entry["url"],
        education_level_id=ref_maps["education_levels"][entry["level"]],
        study_form_id=ref_maps["study_forms"][entry["Форма обучения:"]],
        study_duration_id=ref_maps["study_durations"][entry["Срок обучения:"]],
        program_info=entry.get("program_info", ""),
        career_info=entry.get("career_info", ""),
    )


def add_exams(entry: dict, program_id: int, db: AsyncSession, ref_maps: dict):
    for contest_name, subjects_list in entry.get("contest_exams", {}).items():
        contest_id = ref_maps["contest_types"][contest_name.strip()]
        for subject_name in subjects_list:
            is_optional = "на выбор" in subject_name
            clean_subject = subject_name.replace(" (на выбор)", "").strip()
            if clean_subject:
                subject_id = ref_maps["subjects"][clean_subject]
                db.add(
                    ProgramContestExam(
                        program_id=program_id,
                        contest_type_id=contest_id,
                        subject_id=subject_id,
                        is_optional=is_optional,
                    )
                )


def add_score_stats(entry: dict, program_id: int, db: AsyncSession):
    for stat_type, key in [
        ("passing", "place_passing_score"),
        ("mean", "place_mean_score"),
    ]:
        scores = entry.get(key)
        if scores:
            db.add(
                ScoreStat(
                    program_id=program_id,
                    stat_type=stat_type,
                    budget_places=scores.get("Бюжетные места"),
                    target_places=scores.get("Целевые места"),
                    quota_places=scores.get("Места в рамках квоты"),
                    paid_places=scores.get("Платные места"),
                )
            )


async def add_program_timeline_bindings(
    entry: dict, program_id: int, db: AsyncSession, ref_maps: dict
):
    ref_maps["bindings"] = {}

    for endpoint_type in ("budget_endpoints", "paid_endpoints"):
        type_id = ref_maps["timeline_type"][endpoint_type]

        binding = ProgramTimelineBinding(program_id=program_id, type_id=type_id)
        db.add(binding)
        await db.flush()  # нужно, чтобы binding.id был присвоен до коммита

        if endpoint_type not in ref_maps["bindings"]:
            ref_maps["bindings"][endpoint_type] = {}

        ref_maps["bindings"][endpoint_type][program_id] = binding.id


MONTHS_RU = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def parse_russian_date(date_str: str, default_year: int = 2025) -> date | None:
    try:
        parts = date_str.strip().split()
        if len(parts) != 2:
            return None
        day = int(parts[0])
        month = MONTHS_RU.get(parts[1].lower())
        if not month:
            return None
        return date(default_year, month, day)
    except Exception:
        return None


async def add_timeline_events(
    entry: dict, program_id: int, db: AsyncSession, ref_maps: dict
):
    for endpoint_type in ("budget_endpoints", "paid_endpoints"):
        for evt in entry.get(endpoint_type, []):
            name, date_str = next(iter(evt.items()))
            name_id = ref_maps["timeline_name"][name]
            bindings_id = ref_maps["bindings"][endpoint_type][program_id]

            parsed_date = parse_russian_date(date_str)
            if not parsed_date:
                # Можно тут логировать или выбросить ошибку, если дата не распарсилась
                raise Exception("Дата не распарсилась")

            db.add(
                TimelineEvent(
                    binding_id=bindings_id,
                    name_id=name_id,
                    deadline=parsed_date,
                )
            )


async def load_program_data(data: list[dict], db: AsyncSession):
    ref_maps = await load_reference_data(data, db)

    for entry in data:
        if "направленность не предусмотрена" in entry.get("title", ""):
            continue
        program = create_program(entry, ref_maps)

        db.add(program)
        await db.flush()

        add_exams(entry, program.id, db, ref_maps)
        add_score_stats(entry, program.id, db)
        await add_program_timeline_bindings(entry, program.id, db, ref_maps)
        await add_timeline_events(entry, program.id, db, ref_maps)

    await db.commit()


async def main():
    engine = create_async_engine(
        db_settings.get_connection_url(),
        future=True,
    )
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with session_factory() as session:
        await load_program_data(data, db=session)


if __name__ == "__main__":
    asyncio.run(main())
