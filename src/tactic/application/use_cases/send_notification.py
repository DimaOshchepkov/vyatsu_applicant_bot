from datetime import datetime

from tactic.application.services.message_sender import MessageSender


class SendNotificationUseCase:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    async def __call__(self, chat_id: int, text: str, delay: float) -> None:
        await self.sender.send_delay(chat_id, text, delay)
