import logging
from typing import Any, List, Optional

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

    exam_id_int = int(exam_id)
    data.collected_subjects[exam_id_int] = data.id_to_subject[exam_id_int]

    data.update_manager(dialog_manager)

    await callback.message.answer(
        f"Добавлен экзамен: {data.id_to_subject[exam_id_int]}"
    )
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
        matched_subjects = await recognize_exam_usecase(user_input=data, k=3)

    if not matched_subjects or len(matched_subjects) == 0:
        await message.answer("Не найдено экзаменов, попробуйте ещё раз.")
        await dialog_manager.done()
        return

    exams_data = ExamDialogData.from_manager(dialog_manager)
    exams_data.id_to_subject = {subj.id: subj.model_dump() for subj in matched_subjects}
    exams_data.update_manager(dialog_manager)

    await dialog_manager.switch_to(ExamDialog.choose_match)


async def on_finish_handler(
    callback: CallbackQuery, button: Any, dialog_manager: DialogManager
):
    data = ExamDialogData.from_manager(dialog_manager)
    if not data.collected_subjects:
        await callback.message.answer("Вы ещё ничего не ввели.")
        await dialog_manager.done()
        return

    text = "Вы выбрали:\n" + "\n".join(f"• {e}" for e in data.collected_subjects)
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
    def as_list(value: Optional[int]) -> Optional[List[int]]:
        return [value] if value is not None else None

    data = ExamDialogData.from_manager(dialog_manager)

    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]
    async with ioc.get_filtered_programs() as get_programs:
        subj_ids = list(data.collected_subjects.keys()) if data.collected_subjects else []
        filtered_programs = await get_programs(
            study_form_ids=as_list(data.study_form_id),
            education_level_ids=as_list(data.education_level_id),
            contest_type_ids=as_list(data.contest_type_id),
            exam_subject_ids=subj_ids,
        )

    programs = await get_recommended_programs(
        SearchRequestDTO(query=data_input, k=5, programs_id=filtered_programs)
    )

    data.programs = [p.model_dump() for p in programs]
    data.update_manager(dialog_manager)

    await dialog_manager.switch_to(ExamDialog.show_programs)


async def on_education_level_chosen(
    callback: CallbackQuery, widget: Any, manager: DialogManager, id: str
):
    data = ExamDialogData.from_manager(manager)
    data.education_level_id = int(id)
    data.update_manager(manager)

    await manager.next()


async def on_contest_type_chosen(
    callback: CallbackQuery, widget: Any, manager: DialogManager, id: str
):
    data = ExamDialogData.from_manager(manager)
    data.contest_type_id = int(id)
    data.update_manager(manager)
    await manager.next()


async def on_study_form_chosen(
    callback: CallbackQuery, widget: Any, manager: DialogManager, id: str
):
    data = ExamDialogData.from_manager(manager)
    data.study_form_id = int(id)
    data.update_manager(manager)
    await manager.next()


async def on_back(callback: CallbackQuery, button: Any, manager: DialogManager):
    if manager.current_context().state == ExamDialog.input_interests:
        await manager.switch_to(ExamDialog.input_exam)
        return
    await manager.back()


async def on_skip(callback: CallbackQuery, button: Any, manager: DialogManager):
    if manager.current_context().state == ExamDialog.input_exam:
        await manager.switch_to(ExamDialog.input_interests)
        return
    await manager.next()
