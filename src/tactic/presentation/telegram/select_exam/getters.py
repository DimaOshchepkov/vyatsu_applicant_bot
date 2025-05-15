from typing import Any

from aiogram_dialog import DialogManager

from tactic.presentation.telegram.select_exam.context import (
    ExamDialogData,
    MatchedExamsContext,
    MatchItem,
)
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
