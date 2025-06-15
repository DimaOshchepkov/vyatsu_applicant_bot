from typing import Optional, Union

from aiogram.types import Message
from aiogram.types.inaccessible_message import InaccessibleMessage
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery


def require_message(message: Optional[Union[Message, InaccessibleMessage]]):
    if message is None:
        raise ValueError("Expected callback.message to be present")
    return message


def get_message_or_raise(manager: DialogManager):
    event = manager.event
    if isinstance(event, Message):
        return event
    if isinstance(event, CallbackQuery):
        if event.message and not isinstance(event.message, InaccessibleMessage):
            return event.message
    raise ValueError("Невозможно получить Message из события")


def get_user_id_or_raise(manager: DialogManager) -> int:
    event = manager.event
    if isinstance(event, Message):
        if not event.from_user:
            raise ValueError("Не удалось получить user_id из сообщения")
        return event.from_user.id
    if isinstance(event, CallbackQuery):
        if not event.from_user:
            raise ValueError("Не удалось получить user_id из callback")
        return event.from_user.id
    raise ValueError("Неизвестный тип события")

def get_chat_id_or_raise(manager: DialogManager) -> int:
    event = manager.event

    if isinstance(event, Message):
        return event.chat.id
    if isinstance(event, CallbackQuery):
        if event.message and not isinstance(event.message, InaccessibleMessage):
            return event.message.chat.id

    raise ValueError("Невозможно получить chat_id из события")
