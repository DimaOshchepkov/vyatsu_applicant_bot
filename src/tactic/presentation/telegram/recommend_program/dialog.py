from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.recommend_program.context import ExamDialogData
from tactic.presentation.telegram.recommend_program.ui import (
    choose_match_window,
    contest_type_window,
    education_level_window,
    input_exam_window,
    input_interests_window,
    show_programs_window,
    study_form_window,
)
from tactic.presentation.telegram.states import ExamDialog


async def on_exam_start(start_data, manager: DialogManager, **kwargs):
    # Устанавливаем начальные значения сразу при старте диалога
    manager.dialog_data["current_step"] = 1
    manager.dialog_data["total_steps"] = 5


async def start_recommendatory_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(
        ExamDialog.choose_education_level,
        mode=StartMode.RESET_STACK,
    )


recommendatory_dialog = Dialog(
    education_level_window,
    study_form_window,
    contest_type_window,
    input_exam_window,
    choose_match_window,
    input_interests_window,
    show_programs_window,
    on_start=on_exam_start,
)
