from dataclasses import dataclass
from typing import Callable

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_dialog import Dialog

from tactic.presentation.telegram.create_notification.dialog import (
    notification_dialog,
    start_notification_dialog,
)
from tactic.presentation.telegram.new_user.dialog import start_dialog, user_start
from tactic.presentation.telegram.recommend_program.dialog import (
    recommendatory_dialog,
    start_recommendatory_dialog,
)
from tactic.presentation.telegram.select_question_category.dialog import (
    categories_and_questions_dialog,
    start_category_dialog,
)


@dataclass
class CommandSpec:
    name: str
    description: str
    handler: Callable
    dialog: Dialog


COMMANDS = [
    CommandSpec("start", "Начать", user_start, start_dialog),
    CommandSpec(
        "recommend",
        "Получить рекомендации",
        start_recommendatory_dialog,
        recommendatory_dialog,
    ),
    CommandSpec(
        "question",
        "Задать вопрос о поступлении",
        start_category_dialog,
        categories_and_questions_dialog,
    ),
    CommandSpec(
        "notification",
        "Наcтроить уведомления",
        start_notification_dialog,
        notification_dialog,
    ),
]


def register_handlers(dp: Dispatcher):
    for cmd in COMMANDS:
        dp.message.register(cmd.handler, Command(commands=cmd.name))


def register_dialogs(dp: Dispatcher) -> None:
    for cmd in COMMANDS:
        dp.include_router(cmd.dialog)


async def register_commands(bot: Bot):
    commands = [BotCommand(command=c.name, description=c.description) for c in COMMANDS]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


__all__ = [
    "register_handlers",
    "register_dialogs",
    "register_commands",
]
