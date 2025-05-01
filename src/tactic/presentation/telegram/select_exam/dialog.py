import logging
from typing import Any, Dict, List, Tuple
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Select, Column
from aiogram_dialog.widgets.text import Format
from aiogram.types import CallbackQuery, Message

from slugify import slugify

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.states import ExamDialog


def to_id(s: str):
    return slugify(s)[:50]
    
    
# -------------------------------
# ⚙️ Настройка логгера
# -------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# -------------------------------
# ✂️ Функция сокращения названия экзамена
# -------------------------------
def truncate_tail(text: str, max_len: int = 32) -> str:
    return text if len(text) <= max_len else "..." + text[-(max_len - 3):]

# -------------------------------
# 🎬 Старт диалога
# -------------------------------
async def start_exam_dialog(message: Message, ioc: InteractorFactory, dialog_manager: DialogManager):
    logger.debug("Starting exam dialog")
    await dialog_manager.start(ExamDialog.input_exam)

# -------------------------------
# 📦 Getter — возвращает список экзаменов
# -------------------------------
async def exams_getter(dialog_manager: DialogManager,
                       **kwargs: Any) -> Dict[str, Dict[str, List[str] | str]]:
    
    
    original_exams = dialog_manager.start_data.get("exams", [])
    exams = [
        {
            "id": to_id(name),  # Безопасный ID
            "title": truncate_tail(name),  # Отображаемое название
        }
        for name in original_exams
    ]
    
    logger.debug(f"Getter returned exams: {exams}")
    return {"exams": exams}

# -------------------------------
# ✅ Обработка выбора экзамена
# -------------------------------
async def on_exam_chosen(
    event: CallbackQuery,
    select: Any,
    dialog_manager: DialogManager,
    id: str,
):
    
    id_to_exam = dialog_manager.start_data["id_to_exam"]
    logger.debug(f"User selected exam: {id_to_exam[id]}")
    await event.message.answer(f"Вы выбрали экзамен: {id_to_exam[id]}")
    await dialog_manager.done()

# -------------------------------
# 🪪 Окно выбора экзамена
# -------------------------------
choose_exam_window = Window(
    Format("Выберите экзамен:"),
    Column(Select(
        text=Format("{item[title]}"),
        id="exam_select",
        item_id_getter=lambda item: item["id"],
        items="exams",
        on_click=on_exam_chosen,
    )),
    getter=exams_getter,
    state=ExamDialog.choose_exam,
)

# -------------------------------
# 🎯 Обработка текстового ввода экзамена
# -------------------------------
async def exam_input_handler(
    message: Message,
    widget: ManagedTextInput[str],
    dialog_manager: DialogManager,
    data: str,
):
    logger.debug(f"User input received: {data}")
    
    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]

    async with ioc.recognize_exam() as recognize_exam_usecase:
        matched_exams = await recognize_exam_usecase(user_input=message.text, k=3)

    logger.debug(f"Matched exams: {matched_exams}")

    if not matched_exams:
        await message.answer("Не найдено экзаменов, попробуйте ещё раз.")
        return
    
    id_to_exam = { to_id(name) : name for name in matched_exams}

    await dialog_manager.start(
        ExamDialog.choose_exam,
        data={"exams": matched_exams, "id_to_exam": id_to_exam},
        mode=StartMode.RESET_STACK,
    )

# -------------------------------
# ⌨️ Окно текстового ввода
# -------------------------------
input_exam_window = Window(
    Format("Введите название экзамена:"),
    TextInput(id="exam_input", on_success=exam_input_handler),
    state=ExamDialog.input_exam,
)

# -------------------------------
# 🧩 Диалог
# -------------------------------
exam_dialog = Dialog(
    input_exam_window,
    choose_exam_window,
)
