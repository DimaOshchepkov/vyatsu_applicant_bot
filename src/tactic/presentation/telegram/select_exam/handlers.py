from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.select_exam.context import ExamDialogData
from tactic.presentation.telegram.select_exam.utils import to_id
from tactic.presentation.telegram.states import ExamDialog


async def on_exam_chosen_handler(
    callback: CallbackQuery,
    select: Any,
    dialog_manager: DialogManager,
    exam_id: str,
):
    data = ExamDialogData.from_manager(dialog_manager)
    exam_id_int = int(exam_id)

    if data.id_to_exam[exam_id_int] not in data.collected_exams:
        data.collected_exams.append(data.id_to_exam[exam_id_int])

    data.update_manager(dialog_manager)

    await callback.message.answer(f"Добавлен экзамен: {data.id_to_exam[exam_id_int]}")
    await dialog_manager.switch_to(ExamDialog.input_exam, show_mode=ShowMode.SEND)


async def exam_input_handler(
    message: Message,
    widget: Any,
    dialog_manager: DialogManager,
    data: str,
):
    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]

    async with ioc.recognize_exam() as recognize_exam_usecase:
        matched_exams = await recognize_exam_usecase(user_input=data, k=3)

    if not matched_exams or len(matched_exams) == 0:
        await message.answer("Не найдено экзаменов, попробуйте ещё раз.")
        return

    exams_data = ExamDialogData.from_manager(dialog_manager)
    exams_data.last_matches = matched_exams
    exams_data.id_to_exam = {to_id(i): exam for i, exam in enumerate(matched_exams)}
    exams_data.update_manager(dialog_manager)

    await dialog_manager.switch_to(ExamDialog.choose_match)


async def on_finish_handler(
    callback: CallbackQuery, button: Any, dialog_manager: DialogManager
):
    data = ExamDialogData.from_manager(dialog_manager)
    if not data.collected_exams:
        await callback.message.answer("Вы ещё ничего не ввели.")
        return

    text = "Вы выбрали:\n" + "\n".join(f"• {e}" for e in data.collected_exams)
    await callback.message.answer(text)
    await dialog_manager.done()


async def on_cancel_handler(
    callback: CallbackQuery, button: Any, dialog_manager: DialogManager
):
    await callback.message.answer("Ввод экзаменов отменён.")
    await dialog_manager.done()
