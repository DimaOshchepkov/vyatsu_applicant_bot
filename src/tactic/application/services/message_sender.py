from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from tactic.domain.entities.timeline_event import TimelineEventDTO


class MessageSender(ABC):
    """
    Абстрактный базовый класс для отправителей сообщений.
    """

    @abstractmethod
    async def schedule_message(self, chat_id: int, event: TimelineEventDTO) -> None: ...

    @abstractmethod
    async def cancel_scheduled_message(self, chat_id: int, event: TimelineEventDTO): ...

    @abstractmethod
    async def schedule_messages_bulk(
        self, chat_id: int, events: List[TimelineEventDTO]
    ): ...
    @abstractmethod
    async def cancel_scheduled_messages_bulk(
        self, chat_id: int, events: List[TimelineEventDTO]
    ): ...
