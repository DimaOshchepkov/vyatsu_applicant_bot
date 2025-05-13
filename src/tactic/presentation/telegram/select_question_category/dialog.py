# dialog.py
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Select, Cancel, Column
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog import StartMode
from aiogram.types import Message
from typing import Optional, List
from tactic.domain.entities.category import CategoryDomain
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.cache import CategoryCache
from tactic.presentation.telegram.states import CategoryStates
from aiogram.types import CallbackQuery
from typing import Any



# Генерация списка категорий
async def category_getter(dialog_manager: DialogManager, **kwargs):
    
    parent_id = dialog_manager.dialog_data.get("parent_id")
    
    all_categories = CategoryCache.get()
    if all_categories is None:
        return {"categories": [], "path": []}
        
    categories = [cat for cat in all_categories if cat.parent_id == parent_id]
    
    return {
        "categories": categories,
        "path": dialog_manager.dialog_data.get("path", []),
    }

# Обработка выбора категории
async def on_category_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    
    selected_id = int(item_id)
    
    all_categories = CategoryCache.get()
    if all_categories is None:
        return 
        
    selected_category = next((c for c in all_categories if c.id == selected_id), None)
    if not selected_category:
        return

    # Обновим текущую категорию
    manager.dialog_data["parent_id"] = selected_category.id
    path: List[str] = manager.dialog_data.get("path", [])
    path.append(selected_category.title)
    manager.dialog_data["path"] = path

    await manager.switch_to(CategoryStates.browsing)

# Виджет выбора категории
category_select = Column(Select(
    Format("{item.title}"),
    id="category_select",
    item_id_getter=lambda c: str(c.id),
    items="categories",
    on_click=on_category_selected)
)

# Диалог
category_dialog = Dialog(
    Window(
        Format("Выберите категорию:\n{path}"),
        category_select,
        Cancel(Const("Отмена")),
        state=CategoryStates.browsing,
        getter=category_getter,
    )
)

# Старт диалога
async def start_category_dialog(message: Message, ioc: InteractorFactory, dialog_manager: DialogManager):
    # Генерация списка категорий

    async with ioc.get_categories() as get_categories:
        all_categories = await get_categories()
        CategoryCache.set(all_categories)
        
    await dialog_manager.start(
        CategoryStates.browsing,
        mode=StartMode.RESET_STACK,
        data={"parent_id": None, "path": []}
    )
