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
    message = get_message_or_raise(manager)
    if not message.from_user:
        raise ValueError("Не удалось получить user_id")
    return message.from_user.id
