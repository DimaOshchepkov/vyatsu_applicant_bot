from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from shared.models import EducationLevel
from tactic.infrastructure.db.check_db.check_education_level import (
    check_education_levels,
)
from tactic.infrastructure.db.check_db.table_exist_and_empty import (
    table_exists_and_empty,
)


async def is_correct_education_levels(
    engine: AsyncEngine, session_factory: async_sessionmaker[AsyncSession]
) -> bool:
    if await table_exists_and_empty(engine, EducationLevel):
        async with session_factory() as session:
            async with session.begin():
                errors = await check_education_levels(session)
                if errors:
                    return False
    return True
