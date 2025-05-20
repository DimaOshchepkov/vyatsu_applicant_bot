from typing import List, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Program


class ProgramRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_paginated(
        self, limit: int = 100, offset: int = 0
    ) -> Tuple[Sequence[Program], int]:
        stmt = select(Program).limit(limit).offset(offset)
        result = await self.session.execute(stmt)

        count_stmt = select(func.count()).select_from(Program)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        return result.scalars().all(), total
