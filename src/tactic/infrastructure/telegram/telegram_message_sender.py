from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from arq import create_pool
from arq.connections import RedisSettings

from tactic.application.services.message_sender import MessageSender
from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot
from tactic.settings import redis_settings


class TelegramMessageSender(MessageSender):
    def __init__(self, bot: RateLimitedBot):
        self.bot = bot

    async def send(self, chat_id: int, text: str, when: datetime):
        moscow_tz = ZoneInfo("Europe/Moscow")
        now = datetime.now(tz=moscow_tz)
        delay = (when - now).total_seconds()

        if delay <= 0:
            await self.bot.send_message(chat_id, text)
        else:
            redis = await create_pool(
                RedisSettings(
                    host=redis_settings.redis_host, port=redis_settings.redis_port
                )
            )
            await redis.enqueue_job(
                "send_delayed_message",
                chat_id=chat_id,
                text=text,
                when=when.isoformat(),
                _defer_by=delay,
            )
            await redis.close()

    async def close(self):
        await self.bot.session.close()
