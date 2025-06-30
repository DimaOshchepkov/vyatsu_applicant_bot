from abc import ABC, abstractmethod
from typing import Any, Coroutine, Optional

from aiogram import Bot
from aiogram.methods import GetChat, TelegramMethod
from aiolimiter import AsyncLimiter
from arate_limit import RedisSlidingWindowRateLimiter
from cachetools import TTLCache  # type:ignore
from redis.asyncio import Redis


class LimiterBackend(ABC):
    @abstractmethod
    async def call_with_limit(self, chat_id: int, coro: Coroutine) -> Any: ...


class RedisLimiterBackend(LimiterBackend):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.global_limiter = RedisSlidingWindowRateLimiter(
            redis=self.redis,
            event_count=30,
            time_window=1,
            slack=0,
        )
        self.chats = TTLCache[int, RedisSlidingWindowRateLimiter](
            maxsize=100_000, ttl=60
        )
        self.groups = TTLCache[int, RedisSlidingWindowRateLimiter](
            maxsize=100_000, ttl=60
        )

    async def call_with_limit(
        self, chat_id: int, coro: Coroutine[Any, Any, Any]
    ) -> Any:

        if chat_id < 0:
            limiter = self.groups.get(chat_id)
            if limiter is None:
                limiter = RedisSlidingWindowRateLimiter(
                    redis=self.redis,
                    event_count=20,
                    time_window=60,
                    slack=0,
                )
                self.groups[chat_id] = limiter
        else:
            limiter = self.chats.get(chat_id)
            if limiter is None:
                limiter = RedisSlidingWindowRateLimiter(
                    redis=self.redis,
                    event_count=1,
                    time_window=1,
                    slack=3,
                )
                self.chats[chat_id] = limiter

        await self.global_limiter.wait()
        await limiter.wait()
        return await coro


class InMemoryLimiterBackend(LimiterBackend):
    def __init__(self):
        # Глобальный лимит: 30 запросов/сек
        self.global_limiter = AsyncLimiter(30)

        # Кэш лимитеров для чатов и групп (временные)
        self.chats = TTLCache[int, AsyncLimiter](maxsize=100_000, ttl=60)
        self.groups = TTLCache[int, AsyncLimiter](maxsize=100_000, ttl=60)

    async def call_with_limit(self, chat_id: int, coro: Coroutine) -> Any:
        async with self.global_limiter:
            if chat_id < 0:
                return await self._with_scoped_limit(
                    chat_id, coro, self.groups, 0.32, 20
                )
            else:
                return await self._with_scoped_limit(chat_id, coro, self.chats, 0.99, 1)

    async def _with_scoped_limit(
        self,
        chat_id: int,
        coro: Coroutine,
        storage: TTLCache[int, AsyncLimiter],
        rate: float,
        burst: int,
    ) -> Any:
        limiter = storage.get(chat_id)
        if limiter is None:
            limiter = AsyncLimiter(rate, burst)
            storage[chat_id] = limiter

        async with limiter:
            return await coro


class RateLimitedBot(Bot):
    def __init__(
        self,
        *args,
        limiter_backend: LimiterBackend = InMemoryLimiterBackend(),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.limiter_backend = limiter_backend

    async def __call__(
        self, method: TelegramMethod[Any], request_timeout: Optional[int] = None
    ):
        chat_id = getattr(method, "chat_id", None)
        if chat_id is not None and not isinstance(method, GetChat):
            return await self.limiter_backend.call_with_limit(
                chat_id, self.session(self, method, timeout=request_timeout)
            )
        else:
            return await self.session(self, method, timeout=request_timeout)


def patch_bot(limiter_backend: Optional[LimiterBackend] = None):
    if limiter_backend is None:
        limiter_backend = InMemoryLimiterBackend()

    original_init = Bot.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.limiter_backend = limiter_backend

    Bot.__call__ = RateLimitedBot.__call__  # type: ignore[assignment]
    Bot.__init__ = new_init  # type: ignore[assignment]
