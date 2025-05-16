import asyncio
import pytest
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


from shared.models import Base
from tests.settings import settings




DATABASE_URL = settings.get_connection_url()


async_engine = create_async_engine(
    DATABASE_URL, poolclass=NullPool,
)


async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
async def db_session():
    async with async_session() as session:
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            
        yield session
        

        
        