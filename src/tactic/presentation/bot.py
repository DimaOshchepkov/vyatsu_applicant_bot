import logging
import sys

import uvloop
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from aiogram_dialog import setup_dialogs
from arq import create_pool
from arq.connections import RedisSettings

from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_async_sessionmaker, get_engine
from tactic.infrastructure.db.migrations.upload_data.is_correct_timeline_type import (
    is_correct_timeline_type,
)
from tactic.infrastructure.middlewares.antiflood_middlewares import (
    CallbackQueryThrottlingMiddleware,
    MessageThrottlingMiddleware,
)
from tactic.infrastructure.recognize_program_rapid_wuzzy import (
    RecognizeProgramRapidWuzzy,
)
from tactic.infrastructure.repositories.cache_config import setup_cache
from tactic.infrastructure.repositories.program_repository import ProgramRepositoryImpl
from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot
from tactic.presentation.ioc import IoC
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

    config = load_config()
    engine_factory = get_engine(config.db)
    engine = await anext(engine_factory)
    session_factory = await get_async_sessionmaker(engine)

    if not await is_correct_timeline_type(
        engine=engine, session_factory=session_factory
    ):
        logger.error(
            "Доменная модель TimelineType не сопоставляется с состоянием базы данных"
        )
        sys.exit(1)

    redis = await create_pool(
        RedisSettings(host=redis_settings.redis_host, port=redis_settings.redis_port)
    )

    token = config.bot.api_token
    bot = RateLimitedBot(
        token=token,
        redis_url=redis_settings.get_async_connection_string(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    async with session_factory() as session:
        async with session.begin():
            program_repo = ProgramRepositoryImpl(session)
            programs = await program_repo.get_all_titles()
            recognize_program = await RecognizeProgramRapidWuzzy.create(programs, 70)

    ioc = IoC(
        session_factory=session_factory,
        bot=bot,
        arq_redis=redis,
        recognize_program=recognize_program,
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

        await redis.aclose()
        logging.info("Arq redis pool closed.")

        await storage.close()
        logging.info("Aiogram FSM storage closed.")

        await engine.dispose()


if __name__ == "__main__":
    uvloop.run(main())
