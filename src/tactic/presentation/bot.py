import asyncio
import logging

from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from aiogram_dialog import setup_dialogs

from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_engine
from tactic.infrastructure.middlewares.antiflood_middlewares import (
    CallbackQueryThrottlingMiddleware,
    MessageThrottlingMiddleware,
)
from tactic.infrastructure.repositories.cache_config import setup_cache
from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot
from tactic.presentation.create_ioc import IOCFactory
from tactic.presentation.telegram import (
    register_commands,
    register_dialogs,
    register_handlers,
)
from tactic.settings import redis_settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(logging.INFO)

    config = load_config()

    engine_factory = get_engine(config.db)

    ioc = await IOCFactory.get_ioc()

    token = config.bot.api_token
    bot = RateLimitedBot(
        token=token,
        redis_url=redis_settings.get_async_connection_string(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    storage: RedisStorage = RedisStorage.from_url(
        redis_settings.get_connection_string(),
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp = Dispatcher(
        storage=storage,
        events_isolation=RedisEventIsolation(redis=storage.redis),
        ioc=ioc,
    )
    dp.message.middleware.register(MessageThrottlingMiddleware(redis=storage.redis))
    dp.callback_query.middleware.register(
        CallbackQueryThrottlingMiddleware(redis=storage.redis)
    )

    setup_cache()

    register_handlers(dp)
    register_dialogs(dp)
    await register_commands(bot)

    setup_dialogs(dp)

    try:
        await dp.start_polling(bot)
    finally:
        logging.info("Shutdown..")

        try:
            await anext(engine_factory)
        except StopAsyncIteration:
            logging.info("Exited")


if __name__ == "__main__":
    asyncio.run(main())
