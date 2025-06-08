from typing import Optional

from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_async_sessionmaker, get_engine
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.ioc import IoC


class IOCFactory:
    _instance: Optional["InteractorFactory"] = None

    @classmethod
    async def get_ioc(cls) -> InteractorFactory:
        if cls._instance is None:
            cls._instance = await cls._create_ioc()
        return cls._instance

    @classmethod
    async def _create_ioc(cls) -> InteractorFactory:
        config = load_config()
        engine_factory = get_engine(config.db)
        engine = await anext(engine_factory)
        session_factory = await get_async_sessionmaker(engine)
        return IoC(session_factory=session_factory)
