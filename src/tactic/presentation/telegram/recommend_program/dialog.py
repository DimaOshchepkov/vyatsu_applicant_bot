from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.recommend_program.ui import (
    choose_match_window,
    input_exam_window,
    input_interests_window,
    show_programs_window,
)
from tactic.presentation.telegram.states import ExamDialog


async def start_recommendatory_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(
        ExamDialog.input_exam,
        mode=StartMode.RESET_STACK,
    )


recommendatory_dialog = Dialog(
    input_exam_window,
    choose_match_window,
    show_programs_window,
    input_interests_window,
)
