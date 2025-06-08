from abc import ABC, abstractmethod
from datetime import datetime


class MessageSender(ABC):
    @abstractmethod
    async def send(self, chat_id: int, text: str, when: datetime) -> None: ...
