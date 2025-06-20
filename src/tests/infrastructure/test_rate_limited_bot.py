import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot

from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot
from tests.settings import test_redis_settings

token = "1234567890:TEST_TOKEN_FAKE1234567890abcdef"


@pytest.mark.asyncio
async def test_rate_limited_bot_does_not_exceed_global_limit():
    # Устанавливаем лимит: не больше 30 сообщений в секунду
    global_limit = 30
    message_count = 60  # Попробуем отправить 60 сообщений
    chat_id = 123456

    bot = RateLimitedBot(
        token=token,
        redis_url=test_redis_settings.get_async_connection_string(),
        global_rate=global_limit,
        global_per=1.0,
        chat_rate=1000,  # не ограничиваем по chat_id, только global
        chat_per=1.0,
    )

    # Мокаем настоящий send_message
    with patch.object(
        Bot, "send_message", new=AsyncMock(return_value="Mocked Telegram Message")
    ):
        start = time.perf_counter()

        # Отправляем сообщения параллельно
        await asyncio.gather(
            *[
                bot.send_message(chat_id=chat_id, text=f"Test {i}")
                for i in range(message_count)
            ]
        )

        end = time.perf_counter()
        elapsed = end - start

        # Бот не мог отправить быстрее, чем message_count / global_limit
        expected_min_time = (message_count - global_limit) / global_limit

        print(f"Elapsed: {elapsed:.2f} sec, Expected ≥ {expected_min_time:.2f} sec")
        assert elapsed >= expected_min_time - 0.2  # небольшой допуск на погрешность
