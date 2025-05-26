from typing import Any, List

import httpx
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput

from tactic.domain.entities.question import QuestionDomain
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.select_question_category.context import DialogData
from tactic.presentation.telegram.select_question_category.dto import (
    ResponseEntry,
    SearchRequest,
    VectorSearchResponse,
)
from tactic.presentation.telegram.states import CategoryStates
from tactic.settings import vector_db_service_settings


async def on_category_selected(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    selected_id = int(item_id)
    data = DialogData.from_manager(manager)

    ioc: InteractorFactory = manager.middleware_data['ioc']
    async with ioc.get_categories() as get_categories:
        all_categories = await get_categories()

    selected_category = next((c for c in all_categories if c.id == selected_id), None)
    if not selected_category:
        await manager.done()
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
    if 1 <= index <= len(questions):
        selected = questions[index - 1]
        await callback.message.answer(f"Ответ: {selected.answer}")
        
        
async def on_question_from_vector_db_selected(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    index = int(item_id)
    data = DialogData.from_manager(manager)
    questions = [ResponseEntry.model_validate(q) for q in data.search_results]
    if 1 <= index <= len(questions):
        selected = questions[index - 1]
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

    ioc: InteractorFactory = dialog_manager.middleware_data['ioc']
    async with ioc.get_categories() as get_categories:
        all_categories = await get_categories()

    has_children = any(cat.parent_id == data.parent_id for cat in all_categories)

    if has_children:
        await dialog_manager.switch_to(CategoryStates.browsing)
    else:
        await dialog_manager.switch_to(CategoryStates.questions)


async def call_vector_search(request: SearchRequest) -> List[ResponseEntry]:
    url = f"{vector_db_service_settings.get_connection_string()}/search"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=request.model_dump())
        response.raise_for_status()
        return VectorSearchResponse.model_validate(response.json()).results


async def on_question_input(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
):
    data = DialogData.from_manager(manager)
    if not message.text:
        await manager.done()
        return
    user_input = message.text
    data.search_query = user_input

    request = SearchRequest(query=user_input, path=data.path)
    response = await call_vector_search(request)
    data.search_results = [entry.model_dump() for entry in response]
    
    data.update_manager(manager)
    
    await manager.switch_to(CategoryStates.search_results)
