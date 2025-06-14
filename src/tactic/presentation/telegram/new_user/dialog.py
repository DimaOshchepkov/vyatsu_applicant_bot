from datetime import datetime, timedelta

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

from tactic.application.use_cases.create_user import UserInputDTO, UserOutputDTO
from tactic.domain.entities.timeline_event import SendEvent, TimelineEventDTO
from tactic.domain.value_objects.user import UserId
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.require_message import require_message
from tactic.presentation.telegram.states import (
    CategoryStates,
    ExamDialog,
    NewUser,
    ProgramStates,
)

OPTIONS_KEY = "options"


async def user_start(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
) -> None:
    async with ioc.create_user() as create_user:
        user_data: UserOutputDTO = await create_user(
            UserInputDTO(
                user_id=UserId(message.from_user.id),  # type:ignore
            )
        )

    await dialog_manager.start(
        NewUser.user_id,
        mode=StartMode.RESET_STACK,
    )


# --- Обработчики кнопок ---
async def start_exam_dialog(callback, button, manager: DialogManager):
    await manager.start(ExamDialog.choose_education_level, mode=StartMode.RESET_STACK)


async def start_category_dialog(callback, button, manager: DialogManager):
    await manager.start(CategoryStates.browsing, mode=StartMode.RESET_STACK)


async def on_notification(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    ioc: InteractorFactory = manager.middleware_data["ioc"]
    async with ioc.send_telegram_notification() as send_notification:
        when = datetime.now() + timedelta(seconds=3)
        timeline = SendEvent(
            id=-1,
            message="Тест",
            when=when,
        )
        await send_notification(
            chat_id=require_message(callback.message).chat.id,
            event=timeline,
        )

    await callback.answer("Сообщение будет отправлено через 3 секунды")


async def start_set_up_notification(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    await manager.start(ProgramStates.InputProgram, mode=StartMode.RESET_STACK)


# --- Главное меню ---
start_window = Window(
    Const("Привет! Выбери, с чего начать:"),
    Column(
        Button(Const("🔍 Подбор программы"), id="to_exam", on_click=start_exam_dialog),
        Button(Const("❓ Частые вопросы"), id="to_faq", on_click=start_category_dialog),
        Button(Const("Тест уведомлений"), id="notification", on_click=on_notification),
        Button(
            Const("Настроить уведомления"),
            id="set_up_notification",
            on_click=start_set_up_notification,
        ),
    ),
    state=NewUser.user_id,
)

start_dialog = Dialog(start_window)
