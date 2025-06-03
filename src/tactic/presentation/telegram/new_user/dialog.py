from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const

from tactic.application.create_user import UserInputDTO, UserOutputDTO
from tactic.domain.value_objects.user import UserId
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.states import CategoryStates, ExamDialog, NewUser

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


# --- Главное меню ---
start_window = Window(
    Const("Привет! Выберите, с чего начать:"),
    Row(
        Button(Const("🔍 Подбор программы"), id="to_exam", on_click=start_exam_dialog),
        Button(Const("❓ Частые вопросы"), id="to_faq", on_click=start_category_dialog),
    ),
    state=NewUser.user_id,
)

start_dialog = Dialog(start_window)
