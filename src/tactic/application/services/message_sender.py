from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from tactic.domain.entities.timeline_event import SendEvent


class MessageSender(ABC):
    """
    Абстрактный базовый класс для отправителей сообщений.
    """

    @abstractmethod
    async def schedule_message(self, chat_id: int, event: SendEvent, job_id: str | None = None) -> None: ...

    @abstractmethod
    async def cancel_scheduled_message(
        self, chat_id: int | None = None, event_id: int | None = None, job_id: str | None = None
    ): ...

