from typing import Any, Dict
from aiogram import Bot
from aiogram.types import Message
from aiolimiter import AsyncLimiter
from typing import override

class RateLimitedBot(Bot):
    def __init__(
        self,
        token: str,
        rate: int = 30,
        per: float = 1,
        chat_rate: int = 3,
        chat_per: float = 3,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Обёртка над Bot с ограничением частоты запросов (rate limiting).

        Ограничения:
        - Глобально: не более `rate` запросов в `per` секунд.
        - По чатам: не более `chat_rate` запросов в `chat_per` секунд для одного чата.

        Args:
            token (str): Токен Telegram-бота.
            rate (int): Глобальный лимит сообщений.
            per (float): Интервал времени для глобального лимита.
            chat_rate (int): Лимит сообщений на чат.
            chat_per (float): Интервал времени для чат-лимита.
            
        См. также документацию родительского метода.
        """
        
        super().__init__(token, *args, **kwargs)
        self.limiter = AsyncLimiter(rate, per)
        self.chat_limiters: Dict[int | str, AsyncLimiter] = {}
        self.chat_rate = chat_rate
        self.chat_per = chat_per

    @override
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        *args: Any,
        **kwargs: Any
    ) -> Message:
        """
        Отправляет сообщение с применением глобального и чатового ограничения частоты.

        Лимиты:
        - Общий (все сообщения бота)
        - Индивидуальный (для каждого чата)

        Args:
            chat_id (int | str): ID чата, куда отправлять сообщение.
            text (str): Текст сообщения.

        Returns:
            Message: Ответ от Telegram API.
        
        См. также документацию родительского метода.
        """

        if chat_id not in self.chat_limiters:
            self.chat_limiters[chat_id] = AsyncLimiter(self.chat_rate, self.chat_per)

        async with self.limiter:
            async with self.chat_limiters[chat_id]:
                return await super().send_message(chat_id, text, *args, **kwargs)