from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from pydantic import BaseModel, Field

from tactic.domain.entities.notification_subscription import NotificationSubscriptionDTO
from tactic.domain.entities.program import ProgramDTO
from tactic.domain.entities.timeline_event import SendEvent
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
    if len(data.programs) < 1:
        await require_message(message).answer(
            "Ничего не нашлось. Попробуйте ввести еще раз"
        )
        await manager.switch_to(ProgramStates.input_program)
        return
    await manager.switch_to(ProgramStates.select_direction)


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
    await manager.switch_to(ProgramStates.choose_payment)


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

    text = "\n\n".join(
        f"📅 <b>{n.event_name}</b>\n"
        + f"⏳ Дедлайн: {n.deadline.strftime('%d.%m.%Y %H:%M')}"
        for n in timelines
    )

    message_text = f"События программы:\n{text}"
    await require_message(callback.message).answer(message_text, parse_mode="HTML")

    await manager.switch_to(
        ProgramStates.confirm_subscribe, show_mode=ShowMode.DELETE_AND_SEND
    )


async def on_subscription(
    callback: CallbackQuery, select: Any, manager: DialogManager, id: str
):
    data = CreateNotificationData.from_manager(manager)
    data.selected_subscription_id = int(id)
    data.update_manager(manager)

    await manager.switch_to(ProgramStates.subscription_settings)


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

    async with ioc.subscribe_for_program() as subscribe_for_program:
        await subscribe_for_program(
            user_id=user_id,
            chat_id=chat_id,
            program_id=data.selected_program_id,
            timeline_type_id=data.selected_payment_id,
        )

    message_text = f"Вы подписаны на события программы"
    await require_message(callback.message).answer(message_text)
    await manager.switch_to(
        ProgramStates.view_subscriptions, show_mode=ShowMode.DELETE_AND_SEND
    )


async def on_subscribe_no(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    await manager.switch_to(ProgramStates.start, show_mode=ShowMode.DELETE_AND_SEND)


async def start_notification_dialog(
    message: Message, ioc: InteractorFactory, dialog_manager: DialogManager
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.start(
        ProgramStates.start,
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
    await manager.switch_to(
        ProgramStates.view_subscriptions, show_mode=ShowMode.DELETE_AND_SEND
    )


async def on_notification(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    ioc: InteractorFactory = manager.middleware_data["ioc"]
    async with ioc.send_telegram_notification() as send_notification:
        when = datetime.now() + timedelta(seconds=3)
        timeline = SendEvent(
            id=-1,
            message="Так будут отправляться уведомления",
            when=when,
        )
        await send_notification(
            chat_id=require_message(callback.message).chat.id,
            event=timeline,
        )

    await callback.answer("Сообщение будет отправлено через 3 секунды")


async def on_view_notifications(
    c: CallbackQuery, button: Button, manager: DialogManager
):
    data = CreateNotificationData.from_manager(manager)
    if not data.selected_subscription_id:
        await c.answer("Что-то пошло не так. Попробуйте позже", show_alert=True)
        await manager.switch_to(
            ProgramStates.view_subscriptions, show_mode=ShowMode.DELETE_AND_SEND
        )
        return

    ioc: InteractorFactory = manager.middleware_data["ioc"]
    async with ioc.get_sheduled_notification() as get_notification:
        notifications = await get_notification(data.selected_subscription_id)

    if not notifications:
        await c.answer("Нет запланированных уведомлений", show_alert=True)
        return

    text = "\n\n".join(
        f"🔔 <b>{n.event_name}</b>\n"
        + f"🕒 Уведомление: {n.send_at.strftime('%d.%m.%Y %H:%M')}\n"
        + f"⏳ Дедлайн: {n.deadline.strftime('%d.%m.%Y')}"
        for n in notifications
    )
    await require_message(c.message).answer(
        f"<b>Ваши уведомления:</b>\n\n{text}", parse_mode="HTML"
    )
    await manager.switch_to(
        ProgramStates.subscription_settings, show_mode=ShowMode.DELETE_AND_SEND
    )


back = SwitchTo(Const("Назад"), id="back", state=ProgramStates.start)

# Главное меню
notification_start_window = Window(
    Const("Что вы хотите сделать?"),
    Column(
        SwitchTo(
            Const("📬 Посмотреть мои подписки"),
            id="btn_view",
            state=ProgramStates.view_subscriptions,
            show_mode=ShowMode.DELETE_AND_SEND,
        ),
        SwitchTo(
            Const("➕ Добавить новую подписку"),
            id="btn_add",
            state=ProgramStates.input_program,
            show_mode=ShowMode.DELETE_AND_SEND,
        ),
        Button(
            Const("🔔 Тест уведомлений"), id="notification", on_click=on_notification
        ),
        to_menu(),
    ),
    state=ProgramStates.start,
)

# Ввод названия программы
input_program_window = Window(
    Const("Введите название программы:"),
    back,
    TextInput(id="program_input", on_success=on_program_input),
    state=ProgramStates.input_program,
)

# Выбор направления
select_direction_window = Window(
    Const("Выберите направление, на которое хотите подписаться:"),
    Column(
        Select(
            Format("{item[title]}"),
            id="direction_select",
            item_id_getter=lambda item: item["id"],
            items="choices",
            on_click=on_direction_selected,
        ),
        back,
    ),
    getter=get_program_choices,
    state=ProgramStates.select_direction,
)

# Выбор типа оплаты
choose_payment_window = Window(
    Const("Выберите тип обучения:"),
    Select(
        Format("{item[title]}"),
        id="payment_select",
        item_id_getter=lambda x: x["payment_type"],
        items="payment_options",
        on_click=on_payment_chosen,
    ),
    back,
    getter=get_payment_options,
    state=ProgramStates.choose_payment,
)

# Подтверждение подписки
confirm_subscribe_window = Window(
    Const("Хотите ли вы подписаться на уведомления о событиях этой программы?"),
    Row(
        Button(Const("Да"), id="subscribe_yes", on_click=on_subscribe_yes),
        Button(Const("Нет"), id="subscribe_no", on_click=on_subscribe_no),
    ),
    state=ProgramStates.confirm_subscribe,
)

# Просмотр подписок
view_subscriptions_window = Window(
    Const("Ваши активные подписки:"),
    Column(
        Select(
            Format("{item[program_title]} — {item[timeline_type_name]}"),
            id="subscriptions",
            item_id_getter=lambda x: x["id"],
            items="subscriptions",
            on_click=on_subscription,
        ),
        back,
    ),
    getter=get_subscriptions,
    state=ProgramStates.view_subscriptions,
)

# Управление подпиской
subscription_settings_window = Window(
    Const("Вы выбрали подписку. Что будем делать?"),
    Column(
        Button(
            Const("📬 Просмотреть уведомления"),
            id="view_notifications",
            on_click=on_view_notifications,
        ),
        Button(Const("🗑 Отписаться"), id="unsubscribe", on_click=on_unsubscribe),
        back,
    ),
    state=ProgramStates.subscription_settings,
)

notification_dialog = Dialog(
    notification_start_window,
    input_program_window,
    select_direction_window,
    choose_payment_window,
    confirm_subscribe_window,
    view_subscriptions_window,
    subscription_settings_window,
)
