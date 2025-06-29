from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

from shared.models import Base


async def table_exists_and_empty(engine: AsyncEngine, model: type[Base]) -> bool:
    async with engine.begin() as conn:

        def sync_check(conn_):
            inspector = inspect(conn_)
            return inspector.has_table(model.__tablename__)

        has_table = await conn.run_sync(sync_check)

        if not has_table:
            return False

        # Выполняем запрос count(*) через обычный async SELECT
        async_sessionmaker_ = async_sessionmaker(engine, expire_on_commit=False)
        async with async_sessionmaker_() as session:
            result = await session.execute(select(func.count()).select_from(model))
            count = result.scalar_one()
            return count == 0
