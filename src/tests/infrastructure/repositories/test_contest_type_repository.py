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
from tactic.infrastructure.repositories.contest_type_repository import (
    ContestTypeRepositoryImpl,
)


@pytest.fixture
async def setup_contest_type_data(db_session: AsyncSession):
    # Справочники
    edu_level_1 = EducationLevel(name="Бакалавриат")
    edu_level_2 = EducationLevel(name="Магистратура")

    study_form_1 = StudyForm(name="Очная")
    study_form_2 = StudyForm(name="Заочная")

    duration = StudyDuration(years="4 года")  # Если требуется

    subject = Subject(name="Математика")  # Требуется по FK

    # Типы конкурсов
    contest_type_1 = ContestType(name="Олимпиада")
    contest_type_2 = ContestType(name="Экзамен")

    db_session.add_all(
        [
            edu_level_1,
            edu_level_2,
            study_form_1,
            study_form_2,
            duration,
            subject,
            contest_type_1,
            contest_type_2,
        ]
    )
    await db_session.flush()

    # Программы
    program_1 = Program(
        title="Программа 1",
        url="url1",
        education_level_id=edu_level_1.id,
        study_form_id=study_form_1.id,
        study_duration_id=duration.id,
    )
    program_2 = Program(
        title="Программа 2",
        url="url2",
        education_level_id=edu_level_2.id,
        study_form_id=study_form_2.id,
        study_duration_id=duration.id,
    )

    db_session.add_all([program_1, program_2])
    await db_session.flush()

    # Привязка программ к типам конкурсов
    exam_1 = ProgramContestExam(
        program_id=program_1.id,
        contest_type_id=contest_type_1.id,
        subject_id=subject.id,
        is_optional=False,
    )
    exam_2 = ProgramContestExam(
        program_id=program_2.id,
        contest_type_id=contest_type_2.id,
        subject_id=subject.id,
        is_optional=False,
    )

    db_session.add_all([program_1, program_2, exam_1, exam_2])
    await db_session.flush()

    return {
        "contest_type_1": contest_type_1,
        "contest_type_2": contest_type_2,
        "edu_level_1": edu_level_1,
        "edu_level_2": edu_level_2,
        "study_form_1": study_form_1,
        "study_form_2": study_form_2,
    }


@pytest.mark.asyncio
async def test_filter_by_study_form_id(
    db_session: AsyncSession, setup_contest_type_data
):
    repo = ContestTypeRepositoryImpl(db_session)
    form_id = setup_contest_type_data["study_form_1"].id

    result = await repo.filter(study_form_ids=[form_id])
    assert result == [setup_contest_type_data["contest_type_1"].id]


@pytest.mark.asyncio
async def test_filter_by_education_level_id(
    db_session: AsyncSession, setup_contest_type_data
):
    repo = ContestTypeRepositoryImpl(db_session)
    level_id = setup_contest_type_data["edu_level_2"].id

    result = await repo.filter(education_level_ids=[level_id])
    assert result == [setup_contest_type_data["contest_type_2"].id]


@pytest.mark.asyncio
async def test_filter_by_both_conditions(
    db_session: AsyncSession, setup_contest_type_data
):
    repo = ContestTypeRepositoryImpl(db_session)
    level_id = setup_contest_type_data["edu_level_1"].id
    form_id = setup_contest_type_data["study_form_1"].id

    result = await repo.filter(study_form_ids=[form_id], education_level_ids=[level_id])
    assert result == [setup_contest_type_data["contest_type_1"].id]


@pytest.mark.asyncio
async def test_filter_no_match(db_session: AsyncSession, setup_contest_type_data):
    repo = ContestTypeRepositoryImpl(db_session)
    result = await repo.filter(study_form_ids=[999])  # Несуществующий ID
    assert result == []
