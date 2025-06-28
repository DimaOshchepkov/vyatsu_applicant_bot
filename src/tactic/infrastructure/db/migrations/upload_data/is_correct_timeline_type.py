from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from shared.models import TimelineType
from tactic.infrastructure.db.migrations.upload_data.check_timeline_type import (
    check_timeline_types,
)
from tactic.infrastructure.db.migrations.upload_data.table_exist_and_empty import (
    table_exists_and_empty,
)


async def is_correct_timeline_type(
    engine: AsyncEngine, session_factory: async_sessionmaker[AsyncSession]
) -> bool:
    if await table_exists_and_empty(engine, TimelineType):
        async with session_factory() as session:
            async with session.begin():
                timeline_errors = await check_timeline_types(session)
                if timeline_errors:
                    return False
    return True
