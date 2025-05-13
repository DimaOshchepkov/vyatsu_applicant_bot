import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


from tactic.infrastructure.db.models import Base, Category
from tactic.infrastructure.repositories.category_repository import CategoryRepositoryImpl
from tests.settings import settings



DATABASE_URL = settings.get_connection_url()


engine = create_async_engine(DATABASE_URL, echo=False)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)