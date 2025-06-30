import asyncio
import time
from unittest.mock import patch

import pytest
from redis.asyncio import Redis

from tactic.infrastructure.telegram.rate_limited_bot import (
    RateLimitedBot,
    RedisLimiterBackend,
)
from tests.settings import test_redis_settings


@pytest.mark.asyncio
async def test_rate_limited_bot_does_not_exceed_global_limit():
    token = "1234567890:TEST_TOKEN_FAKE1234567890abcdef"
    global_limit = 30
    message_count = 90

    # Redis backend с лимитом
    backend = RedisLimiterBackend(
        redis=Redis(
            host=test_redis_settings.redis_host,
            port=test_redis_settings.redis_port,
        )
    )

    bot = RateLimitedBot(token=token, limiter_backend=backend)
    timestamps = []

    async def mocked_session(self, method, timeout=None):
        timestamps.append(time.perf_counter())
        return "ok"

    # Мокаем session именно у экземпляра
    with patch.object(bot, "session", new=mocked_session):
        await asyncio.gather(
            *[
                bot.send_message(chat_id=i, text=f"Test {i}")
                for i in range(message_count)
            ]
        )

    timestamps = sorted(timestamps)[50:]  # отбрасываем возможный «разогрев»
    for i in range(len(timestamps) - global_limit):
        window = timestamps[i + global_limit] - timestamps[i]
        assert (
            window >= 0.95
        ), f"Rate limit violated: {global_limit+1} messages in {window:.2f} sec. i={i}"
