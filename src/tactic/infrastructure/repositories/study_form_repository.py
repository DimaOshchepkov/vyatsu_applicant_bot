from typing import List, Optional

from aiocache import cached
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Program, StudyForm
from tactic.application.common.repositories import StudyFormRepository
from tactic.domain.entities.study_form import CreateStudyFormDomain, StudyFormDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class StudyFormRepositoryImpl(
    BaseRepository[StudyFormDomain, StudyForm, CreateStudyFormDomain],
    StudyFormRepository,
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, StudyFormDomain, StudyForm, CreateStudyFormDomain)

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[StudyFormDomain]:  # type: ignore
        return await super().get_all()

    async def filter(
        self, education_level_ids: Optional[List[int]] = None
    ) -> List[int]:
        stmt = select(StudyForm.id)

        if education_level_ids:
            stmt = (
                stmt.join(StudyForm.programs)
                .where(Program.education_level_id.in_(education_level_ids))
                .distinct()
            )

        result = await self.db.execute(stmt)
        return [id for id in result.scalars().all()]
