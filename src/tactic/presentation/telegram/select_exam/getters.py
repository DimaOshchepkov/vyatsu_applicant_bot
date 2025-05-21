from typing import Any

from aiogram_dialog import DialogManager

from tactic.presentation.telegram.select_exam.context import (
    ExamDialogData,
    MatchedExamsContext,
    MatchItem,
    ProgramsContext,
)
from tactic.presentation.telegram.select_exam.dto import ProgramResponseEntry
from tactic.presentation.telegram.select_exam.utils import truncate_tail


async def matched_exams_getter(dialog_manager: DialogManager, **kwargs: Any) -> dict:
    data = ExamDialogData.from_manager(dialog_manager)
    context = MatchedExamsContext(
        matches=[
            MatchItem(id=id, title=truncate_tail(title))
            for id, title in data.id_to_exam.items()
        ]
    )
    return context.to_dict()


async def programs_getter(dialog_manager: DialogManager, **kwargs: Any) -> dict:
    data = ExamDialogData.from_manager(dialog_manager)
    programs = [ProgramResponseEntry.model_validate(entry) for entry in data.programs]
    return ProgramsContext(programs=programs).to_dict()
