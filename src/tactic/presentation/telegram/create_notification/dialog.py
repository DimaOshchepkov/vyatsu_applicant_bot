from typing import Any, Dict, List, Optional

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from pydantic import BaseModel, Field

from tactic.domain.entities.notification_subscription import NotificationSubscriptionDTO
from tactic.domain.entities.program import ProgramDTO
from tactic.domain.entities.timeline_type import PaymentType
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)
from tactic.presentation.telegram.new_user.utils import to_menu
from tactic.presentation.telegram.safe_wrappers import (
    get_chat_id_or_raise,
    get_user_id_or_raise,
    require_message,
)
from tactic.presentation.telegram.states import NewUser, ProgramStates


class CreateNotificationData(BaseDialogData["CreateNotificationData"]):
    programs: List[Dict[str, Any]] = Field(default_factory=list)
    timelines: List[Dict[str, Any]] = Field(default_factory=list)
    selected_program_id: Optional[int] = None
    selected_payment_id: Optional[int] = None
    selected_subscription_id: Optional[int] = None


class ProgramChoisesContext(BaseViewContext):
    choices: List[ProgramDTO]


class PaymentChoises(BaseModel):
    payment_type: PaymentType
    title: str


class PaymentChoisesContext(BaseViewContext):
    payment_options: List[PaymentChoises] = Field(default_factory=list)


class SubscriptionsContext(BaseViewContext):
    subscriptions: List[NotificationSubscriptionDTO]


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

    await manager.switch_to(ProgramStates.ConfirmSubscribe)


async def on_subscription(
    callback: CallbackQuery, select: Any, manager: DialogManager, id: str
):
    data = CreateNotificationData.from_manager(manager)
    data.selected_subscription_id = int(id)
    data.update_manager(manager)

    await manager.switch_to(ProgramStates.SubscriptionSettings)


async def on_subscribe_yes(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    data = CreateNotificationData.from_manager(manager)
    ioc: InteractorFactory = manager.middleware_data["ioc"]
    user_id = callback.from_user.id
    chat_id = require_message(callback.message).chat.id

    if data.selected_program_id is None or data.selected_payment_id is None:
        await require_message(callback.message).answer(
            "Что-то пошло не так, попробуйте еще раз"
        )
        await manager.done()
        return

    async with ioc.get_timeline_events() as get_timelines:
        timelines = await get_timelines(
            program_id=data.selected_program_id,
            timeline_type_id=data.selected_payment_id,
        )
        data.timelines = [p.model_dump(mode='json') for p in timelines]
        data.update_manager(manager)

    async with ioc.subscribe_for_program() as subscribe_for_program:
        await subscribe_for_program(
            user_id=user_id,
            chat_id=chat_id,
            program_id=data.selected_program_id,
            timeline_type_id=data.selected_payment_id,
        )

    await require_message(callback.message).answer(
        "Вы подписаны! Вот события:\n"
        + "\n".join(f"{e.event_name}: {e.deadline}" for e in timelines)
    )
    await manager.switch_to(ProgramStates.ViewSubscriptions, show_mode=ShowMode.DELETE_AND_SEND)


async def on_subscribe_no(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    await manager.start(NewUser.user_id, mode=StartMode.RESET_STACK)


async def start_notification_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(
        ProgramStates.Start,
        mode=StartMode.RESET_STACK,
    )


async def get_subscriptions(dialog_manager: DialogManager, **kwargs):
    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]

    async with ioc.get_list_subscriptions() as use_case:
        items = await use_case(user_id=get_user_id_or_raise(dialog_manager))

    return SubscriptionsContext(subscriptions=items).to_dict()


async def on_unsubscribe(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    data = CreateNotificationData.from_manager(manager)

    if data.selected_subscription_id is None:
        await callback.answer("Что-то пошло не так. Попробуйте позже.", show_alert=True)
        return

    ioc: InteractorFactory = manager.middleware_data["ioc"]

    async with ioc.unsubscribe_from_program() as use_case:
        await use_case(
            data.selected_subscription_id, chat_id=get_chat_id_or_raise(manager)
        )

    await callback.answer("Вы успешно отписались.")
    # Можно также завершить диалог или обновить экран
    await manager.switch_to(ProgramStates.ViewSubscriptions)


notification_dialog = Dialog(
    Window(
        Const("Что вы хотите сделать?"),
        Column(
            SwitchTo(
                Const("📬 Посмотреть мои подписки"),
                id="btn_view",
                state=ProgramStates.ViewSubscriptions,
            ),
            SwitchTo(
                Const("➕ Добавить новую подписку"),
                id="btn_add",
                state=ProgramStates.InputProgram,
            ),
        ),
        state=ProgramStates.Start,
    ),
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
    Window(
        Const("Хотите ли вы подписаться на уведомления о событиях этой программы?"),
        Row(
            Button(Const("Да"), id="subscribe_yes", on_click=on_subscribe_yes),
            Button(Const("Нет"), id="subscribe_no", on_click=on_subscribe_no),
        ),
        state=ProgramStates.ConfirmSubscribe,
    ),
    Window(
        Const("Ваши активные подписки:"),
        Column(
            Select(
                Format("{item[program_title]} — {item[timeline_type_name]}"),
                id="subscriptions",
                item_id_getter=lambda x: x["id"],
                items="subscriptions",
                on_click=on_subscription,
            ),
        ),
        to_menu(),
        getter=get_subscriptions,
        state=ProgramStates.ViewSubscriptions,
    ),
    Window(
        Const("Вы выбрали подписку. Что будем делать?"),
        Button(Const("Отписаться"), id="unsubscribe", on_click=on_unsubscribe),
        to_menu(),
        state=ProgramStates.SubscriptionSettings,
    ),
)
