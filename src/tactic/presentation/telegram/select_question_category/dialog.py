from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.cache import CategoryCache
from tactic.presentation.telegram.select_question_category.context import DialogData
from tactic.presentation.telegram.select_question_category.ui import (
    category_window,
    question_window,
    search_results_window,
)
from tactic.presentation.telegram.states import CategoryStates

categories_and_questions_dialog = Dialog(
    category_window,
    question_window,
    search_results_window,
)


async def start_category_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):
    async with ioc.get_categories() as get_categories:
        all_categories = await get_categories()
        CategoryCache.set(all_categories)

    await dialog_manager.start(
        CategoryStates.browsing,
        mode=StartMode.RESET_STACK,
        data=DialogData().to_dict(),
    )
