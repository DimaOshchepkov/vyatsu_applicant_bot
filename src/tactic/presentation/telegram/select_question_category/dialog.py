import logging
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.select_question_category.context import DialogData
from tactic.presentation.telegram.select_question_category.ui import (
    category_window,
    question_window,
    search_results_window,
)
from tactic.presentation.telegram.states import CategoryStates


logging.basicConfig(
    level=logging.DEBUG,  # можно поменять на DEBUG при отладке
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

categories_and_questions_dialog = Dialog(
    category_window,
    question_window,
    search_results_window,
)


async def start_category_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):

    await dialog_manager.start(
        CategoryStates.browsing,
        mode=StartMode.RESET_STACK,
    )
