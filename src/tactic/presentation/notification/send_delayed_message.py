from datetime import datetime, timedelta

from arq.connections import RedisSettings, create_pool
from zoneinfo import ZoneInfo

from tactic.presentation.create_ioc import IOCFactory
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.settings import redis_settings


async def send_delayed_message(ctx, chat_id: int, text: str, when: str) -> None:

    when_dt = datetime.fromisoformat(when)
    ioc: InteractorFactory = await IOCFactory.get_ioc()
    async with ioc.send_telegram_notification() as send_notification:
        await send_notification(chat_id, text, when=when_dt)


async def schedule_send_delayed_message(
    chat_id: int, text: str, delay_seconds: int = 3
):
    redis = await create_pool(
        RedisSettings(host=redis_settings.redis_host, port=redis_settings.redis_port)
    )

    moscow_tz = ZoneInfo("Europe/Moscow")
    when = datetime.now(moscow_tz) + timedelta(seconds=delay_seconds)

    await redis.enqueue_job(
        "send_delayed_message",  # название функции
        chat_id,  # параметры
        text,
        when.isoformat(),  # время в ISO формате
    )
