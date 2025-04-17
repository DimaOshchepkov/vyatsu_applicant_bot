from typing import Dict, Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, CallbackQuery
import redis.asyncio.client 
from abc import abstractmethod
from typing import override
import time

def rate_limit(limit: int, key = None):
    """
    Decorator for configuring rate limit and key in different functions.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class BaseThrottlingMiddleware(BaseMiddleware):
    def __init__(self,
                 redis: redis.asyncio.client.Redis,
                 limit = .5,
                 key_prefix = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(redis = redis)

        super(BaseThrottlingMiddleware, self).__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        try:
            await self.on_process_event(event, data)
        except CancelHandler:
            # Cancel current handler
            return

        result = await handler(event, data)

        return result

    @abstractmethod
    async def on_process_event(
        self, 
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        pass

        
    async def throttle_event(self,
                             event: TelegramObject,
                             key: str,
                             limit: float,
                             user_id: int, 
                             chat_id: int) -> None:
        # Use ThrottleManager.throttle method.
        try:
            await self.throttle_manager.throttle(key,
                                                 rate = limit,
                                                 user_id = user_id,
                                                 chat_id = chat_id)
        except Throttled as t:
            # Execute action
            await self.event_throttled(event, t)

            # Cancel current handler
            raise CancelHandler()

  
    async def event_throttled(self,
                              event: TelegramObject,
                              throttled: 'Throttled'):
        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta
        
        bot = event.bot
        if bot is None:
            raise MissingBotError(
                "Event must contain a reference to bot. Make sure event is properly initialized or override this method."
            )
        # Проверяем, что за тип события
        if isinstance(event, Message):
            await bot.send_message(
                chat_id=event.chat.id,
                text=f"Too many requests. Try again in {delta:.2f} seconds."
            )
        elif isinstance(event, CallbackQuery):
            await bot.answer_callback_query(
                text=f"Too many requests.\nTry again in {delta:.2f} seconds.",
                callback_query_id=event.id,
                show_alert=True
            )
        else:
            raise MissingIdInEventError("Unsupported event type. Override this method for the required type yourself")
        
        
class MessageThrottlingMiddleware(BaseThrottlingMiddleware):
    def __init__(self,
                 redis: redis.asyncio.client.Redis,
                 limit = .5,
                 key_prefix = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(redis = redis)

        super().__init__(redis=redis, limit=limit, key_prefix=key_prefix) 

    @override
    async def on_process_event(
        self, 
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:


        if isinstance(event, Message):
            if event.from_user is None:
                return
            user_id = event.from_user.id
            chat_id = event.chat.id
        
        limit = getattr(data["handler"].callback,
                        "throttling_rate_limit", self.rate_limit)
        key = getattr(data["handler"].callback,
                      "throttling_key", f"{self.prefix}_message")

        await self.throttle_event(event = event,
                                  key = key,
                                  limit = limit,
                                  user_id = user_id,
                                  chat_id = chat_id)


class CallbackQueryThrottlingMiddleware(BaseThrottlingMiddleware):
    def __init__(self,
                 redis: redis.asyncio.client.Redis,
                 limit = .5,
                 key_prefix = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(redis = redis)

        super().__init__(redis=redis, limit=limit, key_prefix=key_prefix) 

    @override
    async def on_process_event(
        self, 
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:


        if isinstance(event, CallbackQuery):
            if event.from_user is None:
                return
            if event.message is None:
                return
            user_id = event.from_user.id
            chat_id = event.message.chat.id
        
        limit = getattr(data["handler"].callback,
                        "throttling_rate_limit", self.rate_limit)
        key = getattr(data["handler"].callback,
                      "throttling_key", f"{self.prefix}_message")

        await self.throttle_event(event = event,
                                  key = key,
                                  limit = limit,
                                  user_id = user_id,
                                  chat_id = chat_id)

class ThrottleManager:
    bucket_keys = [
        "RATE_LIMIT", "DELTA",
        "LAST_CALL", "EXCEEDED_COUNT"
    ]
    def __init__(self, redis: redis.asyncio.client.Redis):
        self.redis = redis

    async def throttle(self, key: str, rate: float, user_id: int, chat_id: int):
        now = time.time()
        bucket_name = f'throttle_{key}_{user_id}_{chat_id}'

        data = await self.redis.hmget(bucket_name, self.bucket_keys)  
        data = {
            k: float(v.decode()) 
               if isinstance(v, bytes) 
               else v 
            for k, v in zip(self.bucket_keys, data) 
            if v is not None
        }

        # Calculate
        called = data.get("LAST_CALL", now)
        delta = now - called
        result = delta >= rate or delta <= 0

        # Save result
        data["RATE_LIMIT"] = rate
        data["LAST_CALL"] = now
        data["DELTA"] = delta
        if not result:
            data["EXCEEDED_COUNT"] += 1
        else:
            data["EXCEEDED_COUNT"] = 1

        await self.redis.hmset(bucket_name, data)

        if not result:
            raise Throttled(key=key, chat=chat_id, user=user_id, **data)
        
        return result

class Throttled(Exception):
    def __init__(self, **kwargs):
        self.key = kwargs.pop("key", '<None>')
        self.called_at = kwargs.pop("LAST_CALL", time.time())
        self.rate = kwargs.pop("RATE_LIMIT", None)
        self.exceeded_count = kwargs.pop("EXCEEDED_COUNT", 0)
        self.delta = kwargs.pop("DELTA", 0)
        self.user = kwargs.pop('user', None)
        self.chat = kwargs.pop('chat', None)

    def __str__(self):
        return f"Rate limit exceeded! (Limit: {self.rate} s, " \
               f"exceeded: {self.exceeded_count}, " \
               f"time delta: {round(self.delta, 3)} s)"

class CancelHandler(Exception):
    pass

class MissingBotError(RuntimeError):
    """Выбрасывается, если event не содержит ссылки на bot."""
    pass

class MissingIdInEventError(RuntimeError):
    """Выбрасывается, если нет поля id в event"""
    pass