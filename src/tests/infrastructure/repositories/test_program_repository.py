import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import (
    ContestType,
    EducationLevel,
    Program,
    ProgramContestExam,
    StudyDuration,
    StudyForm,
    Subject,
)
from tactic.infrastructure.repositories.program_repository import ProgramRepositoryImpl


@pytest.fixture
async def seeded_db(db_session: AsyncSession):
    # Справочники
    level1 = EducationLevel(name="Бакалавриат")
    level2 = EducationLevel(name="Магистратура")

    form1 = StudyForm(name="Очная")
    form2 = StudyForm(name="Заочная")

    duration = StudyDuration(years="4 года")

    subj1 = Subject(name="Математика")
    subj2 = Subject(name="Русский язык")

    ctype = ContestType(name="ЕГЭ")

    db_session.add_all([level1, level2, form1, form2, duration, subj1, subj2, ctype])
    await db_session.flush()  # Получаем id

    # Программы
    prog1 = Program(
        title="Программа 1",
        url="http://1.ru",
        education_level=level1,
        study_form=form1,
        study_duration=duration,
    )
    prog2 = Program(
        title="Программа 2",
        url="http://2.ru",
        education_level=level2,
        study_form=form2,
        study_duration=duration,
    )

    db_session.add_all([prog1, prog2])
    await db_session.flush()  # Получаем id программ

    # Экзамены
    exam1 = ProgramContestExam(
        program=prog1,
        contest_type=ctype,
        subject=subj1,
        is_optional=False,
    )
    exam2 = ProgramContestExam(
        program=prog2,
        contest_type=ctype,
        subject=subj2,
        is_optional=False,
    )
    
    exam3 = ProgramContestExam(
        program=prog1,
        contest_type=ctype,
        subject=subj2,
        is_optional=True,
    )


    db_session.add_all([exam1, exam2, exam3])
    await db_session.flush()

    return db_session, {
        "prog1": prog1,
        "prog2": prog2,
        "subj1": subj1,
        "subj2": subj2,
        "ctype": ctype,
        "level1": level1,
        "level2": level2,
        "form1": form1,
        "form2": form2,
        "duration": duration,
    }


@pytest.mark.asyncio
async def test_filter_by_education_level(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(education_level_ids=[data["level1"].id])
    assert result == [data["prog1"].id]


@pytest.mark.asyncio
async def test_filter_by_study_form(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(study_form_ids=[data["form2"].id])
    assert result == [data["prog2"].id]


@pytest.mark.asyncio
async def test_filter_by_exam_subject(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(exam_subject_ids=[data["subj2"].id])
    assert result == [data["prog2"].id]


@pytest.mark.asyncio
async def test_filter_by_contest_type(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(contest_type_ids=[data["ctype"].id])
    assert set(result) == {data["prog1"].id, data["prog2"].id}
    

@pytest.mark.asyncio
async def test_filter_without_filters(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs()
    assert set(result) == {data["prog1"].id, data["prog2"].id}


@pytest.mark.asyncio
async def test_filter_by_nonexistent_ids(seeded_db):
    session, _ = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(education_level_ids=[999])
    assert result == []
    
    
@pytest.mark.asyncio
async def test_filter_by_level_and_form(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(
        education_level_ids=[data["level1"].id],
        study_form_ids=[data["form1"].id],
    )
    assert result == [data["prog1"].id]


@pytest.mark.asyncio
async def test_required_exam_passed(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(
        exam_subject_ids=[data["subj1"].id]
    )
    assert result == []


@pytest.mark.asyncio
async def test_required_exam_missing(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    # subj1 обязателен для prog1, subj2 — другой
    result = await repo.filter_programs(exam_subject_ids=[data["subj2"].id])
    assert result == [data['prog2'].id]
    

@pytest.mark.asyncio
async def test_optional_exam_only(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    result = await repo.filter_programs(
        exam_subject_ids=[data["subj2"].id]
    )
    assert data["prog2"].id in result


@pytest.mark.asyncio
async def test_optional_exists_but_no_match(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    # subj3 — фиктивный, которого нет ни в одной программе
    subj3 = Subject(name="Физика")
    session.add(subj3)
    await session.flush()

    result = await repo.filter_programs(exam_subject_ids=[subj3.id])
    assert result == []

@pytest.mark.asyncio
async def test_multiple_contest_types(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    # Добавим второй тип конкурса
    ctype2 = ContestType(name="Олимпиада")
    session.add(ctype2)
    await session.flush()

    # Программа 1 также может поступать по олимпиаде
    exam_olymp = ProgramContestExam(
        program=data["prog1"],
        contest_type=ctype2,
        subject=data["subj1"],
        is_optional=False,
    )
    session.add(exam_olymp)
    await session.flush()

    result = await repo.filter_programs(contest_type_ids=[data["ctype"].id, ctype2.id])
    assert set(result) == {data["prog1"].id, data["prog2"].id}


@pytest.mark.asyncio
async def test_program_without_any_exams(seeded_db):
    session, data = seeded_db
    repo = ProgramRepositoryImpl(session)

    # Добавим новую программу без экзаменов
    prog3 = Program(
        title="Без экзаменов",
        url="http://noexams.ru",
        education_level=data["level1"],
        study_form=data["form1"],
        study_duration=data["duration"],
    )
    session.add(prog3)
    await session.flush()

    result = await repo.filter_programs(exam_subject_ids=[data["subj1"].id])
    assert prog3.id not in result






