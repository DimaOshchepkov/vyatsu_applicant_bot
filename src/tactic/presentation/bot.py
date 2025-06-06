import asyncio
import logging

from aiogram import Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import (
    DefaultKeyBuilder,
    RedisEventIsolation,
    RedisStorage,
)
from aiogram_dialog import setup_dialogs

from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_async_sessionmaker, get_engine
from tactic.infrastructure.middlewares.antiflood_middlewares import (
    CallbackQueryThrottlingMiddleware,
    MessageThrottlingMiddleware,
)
from tactic.infrastructure.rate_limited_bot import RateLimitedBot
from tactic.infrastructure.repositories.cache_config import setup_cache
from tactic.presentation.ioc import IoC
from tactic.presentation.telegram import register_commands, register_dialogs, register_handlers


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(logging.INFO)

    config = load_config()

    engine_factory = get_engine(config.db)
    engine = await anext(engine_factory)

    session_factory = await get_async_sessionmaker(engine)

    ioc = IoC(session_factory=session_factory)
    token = config.bot.api_token
    bot = RateLimitedBot(token=token, default=DefaultBotProperties(parse_mode="HTML"))

    storage: RedisStorage = RedisStorage.from_url(
        "redis://bot_redis:6379", key_builder=DefaultKeyBuilder(with_destiny=True)
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
