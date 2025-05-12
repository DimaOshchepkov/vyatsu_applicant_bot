import logging
from typing import Any, Dict, List, Tuple
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Select, Column, Button, Row
from aiogram_dialog.widgets.text import Format
from aiogram.types import CallbackQuery, Message


from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.states import ExamDialog


def to_id(index: int) -> int:
    return index
    
    
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def truncate_tail(text: str, max_len: int = 32) -> str:
    return text if len(text) <= max_len else "..." + text[-(max_len - 3):]


async def start_exam_dialog(message: Message, ioc: InteractorFactory, dialog_manager: DialogManager):
    logger.debug("Starting exam dialog")
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(ExamDialog.input_exam, mode=StartMode.RESET_STACK)


async def matched_exams_getter(dialog_manager: DialogManager, **kwargs: Any):
    id_to_exam: dict = dialog_manager.dialog_data.get("id_to_exam", {})
    return {"matches": [{"id": id, "title": truncate_tail(exam)} for id, exam in id_to_exam.items()]}


async def on_exam_chosen(
    callback: CallbackQuery,
    select: Any,
    dialog_manager: DialogManager,
    exam_id: str,
):
    collected = dialog_manager.dialog_data.setdefault("collected_exams", [])
    id_to_exam = dialog_manager.dialog_data.setdefault("id_to_exam", [])
    if id_to_exam[exam_id] not in collected:
        collected.append(id_to_exam[exam_id])

    await callback.message.answer(f"Добавлен экзамен: {id_to_exam[exam_id]}")
    await dialog_manager.switch_to(ExamDialog.input_exam, show_mode=ShowMode.SEND)


async def exam_input_handler(
    message: Message,
    widget: ManagedTextInput[str],
    dialog_manager: DialogManager,
    data: str,
):
    logger.debug(f"User input received: {data}")

    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]

    async with ioc.recognize_exam() as recognize_exam_usecase:
        matched_exams = await recognize_exam_usecase(user_input=data, k=3)

    if not matched_exams:
        await message.answer("Не найдено экзаменов, попробуйте ещё раз.")
        return

    # сохранить найденные экзамены
    dialog_manager.dialog_data["last_matches"] = matched_exams
    dialog_manager.dialog_data["id_to_exam"] = {to_id(id): exam for id, exam in enumerate(matched_exams)}
    await dialog_manager.switch_to(ExamDialog.choose_match)
    

async def on_finish(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    exams = dialog_manager.dialog_data.get("collected_exams", [])
    if not exams:
        await callback.message.answer("Вы ещё ничего не ввели.")
        return

    text = "Вы выбрали:\n" + "\n".join(f"• {e}" for e in exams)
    await callback.message.answer(text)
    await dialog_manager.done()
    
async def on_cancel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer("Ввод экзаменов отменён.")
    await dialog_manager.done()


input_exam_window = Window(
    Format("Введите название экзамена:"),
    TextInput(id="exam_input", on_success=exam_input_handler),
    Row(
        Button(text=Format("✅ Закончить"), id="finish", on_click=on_finish),
        Button(text=Format("❌ Отменить"), id="cancel", on_click=on_cancel),
    ),
    state=ExamDialog.input_exam,
)


choose_match_window = Window(
    Format("Выберите наиболее подходящий экзамен:"),
    Column(
        Select(
            text=Format("{item[title]}"),
            id="match_select",
            item_id_getter=lambda item: item["id"],
            items="matches",
            on_click=on_exam_chosen,
        )
    ),
    getter=matched_exams_getter,
    state=ExamDialog.choose_match,
)


exam_dialog = Dialog(
    input_exam_window,
    choose_match_window,
)
