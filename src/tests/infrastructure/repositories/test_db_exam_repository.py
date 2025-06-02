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
from tactic.infrastructure.repositories.db_exam_repository import DbExamRepository


@pytest.fixture
async def programs_with_exams(db_session: AsyncSession):
    # Создаём связанные сущности
    edu_level = EducationLevel(name="Bachelor")
    study_form = StudyForm(name="Full-time")
    study_duration = StudyDuration(years="4 years")
    contest_type = ContestType(name="mock")

    db_session.add_all([edu_level, study_form, study_duration, contest_type])
    await db_session.flush()

    # Создаём предметы
    math = Subject(name="Math")
    physics = Subject(name="Physics")
    english = Subject(name="English")
    db_session.add_all([math, physics, english])
    await db_session.flush()

    # Создаём программы с обязательными полями
    program1 = Program(
        title="Engineering",
        url="http://example.com/eng",
        education_level_id=edu_level.id,
        study_form_id=study_form.id,
        study_duration_id=study_duration.id,
        program_info="Engineering program description",
        career_info="Engineer, Developer",
    )
    program2 = Program(
        title="Physics",
        url="http://example.com/phys",
        education_level_id=edu_level.id,
        study_form_id=study_form.id,
        study_duration_id=study_duration.id,
        program_info="Physics program description",
        career_info="Physicist, Researcher",
    )
    db_session.add_all([program1, program2])
    await db_session.flush()

    # Добавляем экзамены к программам
    db_session.add_all(
        [
            ProgramContestExam(
                program_id=program1.id,
                subject_id=math.id,
                is_optional=False,
                contest_type_id=contest_type.id,
            ),
            ProgramContestExam(
                program_id=program1.id,
                subject_id=english.id,
                is_optional=True,
                contest_type_id=contest_type.id,
            ),
            ProgramContestExam(
                program_id=program2.id,
                subject_id=physics.id,
                is_optional=False,
                contest_type_id=contest_type.id,
            ),
            ProgramContestExam(
                program_id=program2.id,
                subject_id=english.id,
                is_optional=True,
                contest_type_id=contest_type.id,
            ),
        ]
    )

    await db_session.flush()

    return db_session, {
        "subjects": {
            "math": math,
            "physics": physics,
            "english": english,
        },
        "programs": {
            "program1": program1,
            "program2": program2,
        },
    }


@pytest.mark.asyncio
async def test_get_eligible_program_ids(programs_with_exams):

    db_session, data = programs_with_exams
    subjects = data["subjects"]
    programs = data["programs"]

    # Пользователь сдал Math и English
    subject_ids = {subjects["math"].id, subjects["english"].id}

    repo = DbExamRepository(db_session)
    result = await repo.get_eligible_program_ids(subject_ids)

    # Подходит только программа 1
    assert set(result) == {programs["program1"].id}
