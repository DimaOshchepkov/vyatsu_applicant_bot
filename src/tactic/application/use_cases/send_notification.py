from datetime import datetime

from tactic.application.services.message_sender import MessageSender


class SendNotificationUseCase:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    async def __call__(self, chat_id: int, text: str, when: datetime) -> None:
        await self.sender.send(chat_id, text, when)
