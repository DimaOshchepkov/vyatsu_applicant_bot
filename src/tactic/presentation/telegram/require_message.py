from typing import Optional, Union

from aiogram.types import Message
from aiogram.types.inaccessible_message import InaccessibleMessage


def require_message(message: Optional[Union[Message, InaccessibleMessage]]):
    if message is None:
        raise ValueError("Expected callback.message to be present")
    return message
