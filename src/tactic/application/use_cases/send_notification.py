from datetime import datetime

from tactic.application.services.message_sender import MessageSender
from tactic.domain.entities.timeline_event import SendEvent


class SendNotificationUseCase:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    async def __call__(self, chat_id: int, event: SendEvent) -> None:
        await self.sender.schedule_message(chat_id, event)
