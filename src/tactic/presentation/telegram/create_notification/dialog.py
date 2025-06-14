from typing import Any, Dict, List, Optional

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Select
from aiogram_dialog.widgets.text import Const, Format
from pydantic import BaseModel, Field

from tactic.domain.entities.program import ProgramDTO
from tactic.domain.entities.timeline_type import PaymentType
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)
from tactic.presentation.telegram.new_user.utils import to_menu
from tactic.presentation.telegram.require_message import require_message
from tactic.presentation.telegram.states import ProgramStates


class CreateNotificationData(BaseDialogData["CreateNotificationData"]):
    programs: List[Dict[str, Any]] = Field(default_factory=list)
    timelines: List[Dict[str, Any]] = Field(default_factory=list)
    selected_program_id: Optional[int] = None
    selected_payment_id: Optional[int] = None


class ProgramChoisesContext(BaseViewContext):
    choices: List[ProgramDTO]


class PaymentChoises(BaseModel):
    payment_type: PaymentType
    title: str


class PaymentChoisesContext(BaseViewContext):
    payment_options: List[PaymentChoises] = Field(default_factory=list)


async def on_program_input(
    message: Message,
    widget: Any,
    manager: DialogManager,
    user_input: str,
):
    data = CreateNotificationData.from_manager(manager)
    ioc: InteractorFactory = manager.middleware_data["ioc"]
    async with ioc.recognize_program() as use_case:
        programs = await use_case(user_input)
        data.programs = [p.model_dump() for p in programs]
        data.update_manager(manager)
    await manager.switch_to(ProgramStates.SelectDirection)


async def get_program_choices(dialog_manager: DialogManager, **kwargs):
    data = CreateNotificationData.from_manager(dialog_manager)

    return ProgramChoisesContext(
        choices=[ProgramDTO.model_validate(p) for p in data.programs]
    ).to_dict()


async def on_direction_selected(
    callback_data: CallbackQuery, select: Any, manager: DialogManager, id: str
):
    data = CreateNotificationData.from_manager(manager)
    data.selected_program_id = int(id)
    data.update_manager(manager)
    await manager.switch_to(ProgramStates.ChoosePayment)


async def get_payment_options(dialog_manager: DialogManager, **kwargs):
    return PaymentChoisesContext(
        payment_options=[
            PaymentChoises(payment_type=PaymentType.BUDGET, title="Бюджет"),
            PaymentChoises(payment_type=PaymentType.PAID, title="Платно"),
        ]
    ).to_dict()


async def on_payment_chosen(
    callback: CallbackQuery, select: Any, manager: DialogManager, id: str
):
    data = CreateNotificationData.from_manager(manager)
    data.selected_payment_id = int(id)
    data.update_manager(manager)
    if data.selected_program_id is None or data.selected_payment_id is None:
        await require_message(callback.message).answer(
            "Что-то пошло не так, попробуйте еще раз"
        )
        await manager.done()
        return
    
    ioc: InteractorFactory = manager.middleware_data["ioc"]
    async with ioc.get_timeline_events() as get_timelines:
        timelines = await get_timelines(
            program_id=data.selected_program_id,
            timeline_type_id=data.selected_payment_id,
        )
        data.timelines = [p.model_dump() for p in timelines]
        data.update_manager(manager)
    await require_message(callback.message).answer(
        "Вот события:\n" +
        '\n'.join(f'{e.event_name}: {e.deadline}' for e in timelines)
    )

    await manager.done()


async def start_notification_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(
        ProgramStates.InputProgram,
        mode=StartMode.RESET_STACK,
    )


notification_dialog = Dialog(
    Window(
        Const("Введите название программы:"),
        TextInput(id="program_input", on_success=on_program_input),
        state=ProgramStates.InputProgram,
    ),
    Window(
        Const("Выберите подходящее направление:"),
        Column(
            Select(
                Format("{item[title]}"),
                id="direction_select",
                item_id_getter=lambda item: item["id"],
                items="choices",
                on_click=on_direction_selected,
            )
        ),
        getter=get_program_choices,
        state=ProgramStates.SelectDirection,
    ),
    Window(
        Const("Выберите тип обучения:"),
        Select(
            Format("{item[title]}"),
            id="payment_select",
            item_id_getter=lambda x: x["payment_type"],
            items="payment_options",
            on_click=on_payment_chosen,
        ),
        to_menu(),
        state=ProgramStates.ChoosePayment,
        getter=get_payment_options,
    ),
)
