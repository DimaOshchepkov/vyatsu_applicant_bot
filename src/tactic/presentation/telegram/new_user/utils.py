from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const

from tactic.presentation.telegram.states import NewUser


async def on_to_menu_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.start(NewUser.user_id, mode=StartMode.RESET_STACK)


def to_menu():
    return Button(Const("В меню"), id="menu", on_click=on_to_menu_clicked)
