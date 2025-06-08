import asyncio
from typing import Any, Optional, Union

from aiogram import Bot
from aiogram.types import Message
from limits import RateLimitItemPerSecond
from limits.aio.storage import RedisStorage
from limits.aio.strategies import MovingWindowRateLimiter


class RateLimitedBot(Bot):
    def __init__(
        self,
        token: str,
        redis_url: str,
        global_rate: int = 30,
        global_per: float = 1.0,
        chat_rate: int = 3,
        chat_per: float = 3.0,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(token, *args, **kwargs)
        self.storage = RedisStorage(uri=redis_url)
        self.limiter = MovingWindowRateLimiter(self.storage)

        # лимиты (в сообщениях в секунду)
        self.global_limit = RateLimitItemPerSecond(global_rate)
        self.chat_limit = RateLimitItemPerSecond(chat_rate)

        self.global_per = global_per
        self.chat_per = chat_per

    async def wait_for_slot(
        self, key: str, limit: RateLimitItemPerSecond, interval: float
    ):
        sleep_time = interval / limit.amount
        while True:
            allowed = await self.limiter.test(limit, key)
            if allowed:
                await self.limiter.hit(limit, key)
                return
            await asyncio.sleep(sleep_time)

    async def _apply_rate_limits(self, chat_id: int | str):
        global_key = "rate:global"
        chat_key = f"rate:chat:{chat_id}"
        await self.wait_for_slot(global_key, self.global_limit, self.global_per)
        await self.wait_for_slot(chat_key, self.chat_limit, self.chat_per)

    async def send_message(
        self, chat_id: Union[int, str], text: str, *args: Any, **kwargs: Any
    ) -> Message:
        await self._apply_rate_limits(chat_id)
        return await super().send_message(chat_id, text, *args, **kwargs)

    async def edit_message_text(
        self,
        text: str,
        business_connection_id: str | None = None,
        chat_id: int | str | None = None,
        message_id: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Message | bool:
        # Применяем лимиты
        if chat_id is not None:
            await self._apply_rate_limits(chat_id)
        else:
            await self.wait_for_slot("rate:global", self.global_limit, self.global_per)

        return await super().edit_message_text(
            text,
            business_connection_id,
            chat_id,
            message_id,
            *args,
            **kwargs,
        )
