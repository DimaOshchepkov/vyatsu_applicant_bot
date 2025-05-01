from aiogram import Dispatcher
from aiogram.filters import Command

from tactic.presentation.telegram.select_exam.dialog import start_exam_dialog

from .new_user.dialog import new_user_dialog
from .new_user.dialog import user_start
from .select_exam.dialog import exam_dialog


def register_handlers(dp: Dispatcher) -> None:
    """Register all client-side handlers"""

    dp.message.register(user_start, Command(commands="start"))
    dp.message.register(start_exam_dialog, Command(commands="exam"))


def register_dialogs(dp: Dispatcher) -> None:
    dp.include_router(new_user_dialog)
    dp.include_router(exam_dialog)


__all__ = [
    "register_handlers",
    "register_dialogs",
]
