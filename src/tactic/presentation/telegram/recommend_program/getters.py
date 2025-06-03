from typing import Any

from aiogram_dialog import DialogManager

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.recommend_program.context import (
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
            MatchItem(id=id + 1, title=truncate_tail(name))
            for id, name in data.id_to_exam.items()
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
    return {
        "contest_types": [
            {"id": "ege", "name": "ЕГЭ"},
            {"id": "internal", "name": "Внутренние"},
            {"id": "interview", "name": "Собеседование"},
        ]
    }
