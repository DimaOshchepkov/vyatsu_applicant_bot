from typing import Any

from aiogram_dialog import DialogManager

from tactic.domain.entities.subject import SubjectDomain
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.recommend_program.context import (
    ContestTypesContext,
    EducationLevelContext,
    ExamDialogData,
    MatchedExamsContext,
    MatchItem,
    ProgramsContext,
    StudyFormsContext,
)
from tactic.presentation.telegram.recommend_program.dto import ProgramResponseEntry
from tactic.presentation.telegram.recommend_program.utils import truncate_tail


async def matched_exams_getter(dialog_manager: DialogManager, **kwargs: Any) -> dict:
    data = ExamDialogData.from_manager(dialog_manager)
    context = MatchedExamsContext(
        matches=[
            MatchItem(id=id, title=truncate_tail(SubjectDomain.model_validate(subj).name))
            for id, subj in data.id_to_subject.items()
        ]
    )
    return context.to_dict()


async def programs_getter(dialog_manager: DialogManager, **kwargs: Any) -> dict:
    data = ExamDialogData.from_manager(dialog_manager)
    programs = [ProgramResponseEntry.model_validate(entry) for entry in data.programs]
    return ProgramsContext(programs=programs).to_dict()


async def study_forms_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]
    async with ioc.get_all_study_forms() as study_forms:
        forms = await study_forms()
        context = StudyFormsContext(study_forms=forms)

    return context.to_dict()


async def education_levels_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]
    async with ioc.get_all_education_levels() as education_levels:
        levels = await education_levels()
        context = EducationLevelContext(education_levels=levels)

    return context.to_dict()


async def contest_types_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]
    async with ioc.get_all_contest_types() as contest_types:
        types = await contest_types()
        contest = ContestTypesContext(contest_types=types)

    return contest.to_dict()
