import logging
from typing import Any, List

import httpx
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.recommend_program.context import ExamDialogData
from tactic.presentation.telegram.recommend_program.dto import (
    ProgramResponseEntry,
    SearchRequestDTO,
)
from tactic.presentation.telegram.recommend_program.utils import to_id
from tactic.presentation.telegram.states import ExamDialog
from tactic.settings import vector_db_service_settings

logger = logging.getLogger(__name__)


async def on_exam_chosen_handler(
    callback: CallbackQuery,
    select: Any,
    dialog_manager: DialogManager,
    exam_id: str,
):
    data = ExamDialogData.from_manager(dialog_manager)
    exam_id_int = int(exam_id) - 1

    if data.id_to_exam[exam_id_int] not in data.collected_exams:
        data.collected_exams.append(data.id_to_exam[exam_id_int])

    data.update_manager(dialog_manager)

    await callback.message.answer(f"Добавлен экзамен: {data.id_to_exam[exam_id_int]}")
    await dialog_manager.switch_to(
        ExamDialog.input_exam, show_mode=ShowMode.DELETE_AND_SEND
    )
    
async def on_exam_chosen_from_keyboard_handler(
    message: Message,
    widget: Any,
    dialog_manager: DialogManager,
    exam_id: str,
):
    
    data = ExamDialogData.from_manager(dialog_manager)
    try:
        exam_id_int = int(exam_id)
    except:
        await message.answer("Неправильный номер экзамена. Попробуйте снова")
        await dialog_manager.done()
        return
    
    exam_id_int -= 1
        
    if exam_id_int not in data.id_to_exam.keys():
        await message.answer("Неправильный номер экзамена. Попробуйте снова")
        await dialog_manager.done()
        return

    if data.id_to_exam[exam_id_int] not in data.collected_exams:
        data.collected_exams.append(data.id_to_exam[exam_id_int])

    data.update_manager(dialog_manager)

    await message.answer(f"Добавлен экзамен: {data.id_to_exam[exam_id_int]}")
    await dialog_manager.switch_to(
        ExamDialog.input_exam, show_mode=ShowMode.DELETE_AND_SEND
    )


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
        await dialog_manager.done()
        return

    text = "Вы выбрали:\n" + "\n".join(f"• {e}" for e in data.collected_exams)
    await callback.message.answer(text)
    await dialog_manager.switch_to(ExamDialog.input_interests, show_mode=ShowMode.SEND)
    logger.info("Перешил в состояние input_interests")


async def on_cancel_handler(
    callback: CallbackQuery, button: Any, dialog_manager: DialogManager
):
    await callback.message.answer("Ввод экзаменов отменён.")
    await dialog_manager.done()


async def get_recommended_programs(dto: SearchRequestDTO) -> List[ProgramResponseEntry]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{vector_db_service_settings.get_connection_string()}/programs",
            json=dto.model_dump(),
        )
        response.raise_for_status()
    return [ProgramResponseEntry.model_validate(entry) for entry in response.json()]


async def on_interest_entered_handler(
    message: Message,
    widget: Any,
    dialog_manager: DialogManager,
    data_input: str,
):
    data = ExamDialogData.from_manager(dialog_manager)

    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]
    async with ioc.get_eligible_program_ids() as get_eligible:
        filtered_programs = await get_eligible(set(data.collected_exams))

    programs = await get_recommended_programs(
        SearchRequestDTO(query=message.text, k=5, programs_id=filtered_programs)
    )

    data.programs = programs
    data.update_manager(dialog_manager)

    await dialog_manager.switch_to(ExamDialog.show_programs)
