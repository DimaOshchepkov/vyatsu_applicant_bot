from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from tactic.domain.entities.question import QuestionDomain
from tactic.presentation.telegram.cache import CategoryCache
from tactic.presentation.telegram.select_question_category.context import DialogData
from tactic.presentation.telegram.states import CategoryStates


async def on_category_selected(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    selected_id = int(item_id)
    data = DialogData.from_manager(manager)

    all_categories = CategoryCache.get()
    if all_categories is None:
        return

    selected_category = next((c for c in all_categories if c.id == selected_id), None)
    if not selected_category:
        return

    data.parent_id = selected_category.id
    data.path.append(selected_category.title)
    data.path_id.append(selected_category.id)
    data.update_manager(manager)

    has_children = any(cat.parent_id == selected_category.id for cat in all_categories)

    if has_children:
        await manager.switch_to(CategoryStates.browsing)
    else:
        await manager.switch_to(CategoryStates.questions)


async def on_question_selected(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    index = int(item_id)
    data = DialogData.from_manager(manager)
    questions = [QuestionDomain.model_validate(q) for q in data.last_questions]
    if 0 <= index < len(questions):
        selected = questions[index]
        await callback.message.answer(f"Ответ: {selected.answer}")


async def on_back_clicked(
    callback: CallbackQuery, button: Any, dialog_manager: DialogManager
):
    data = DialogData.from_manager(dialog_manager)

    if data.parent_id is None:
        await dialog_manager.switch_to(CategoryStates.browsing)
        return

    if data.path:
        data.path.pop()
    if data.path_id:
        data.path_id.pop()

    data.parent_id = data.path_id[-1] if data.path_id else None
    data.update_manager(dialog_manager)

    all_categories = CategoryCache.get()
    if all_categories is None:
        await dialog_manager.done()
        return

    has_children = any(cat.parent_id == data.parent_id for cat in all_categories)

    if has_children:
        await dialog_manager.switch_to(CategoryStates.browsing)
    else:
        await dialog_manager.switch_to(CategoryStates.questions)
