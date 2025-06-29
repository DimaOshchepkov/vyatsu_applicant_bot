from typing import List, Optional

from aiocache import cached
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import ContestType, Program, ProgramContestExam
from tactic.application.common.repositories import ContestTypeRepository
from tactic.domain.entities.contest_type import ContestTypeDomain, CreateContestTypeDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class ContestTypeRepositoryImpl(
    BaseRepository[ContestTypeDomain, ContestType, CreateContestTypeDomain], ContestTypeRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContestTypeDomain, ContestType, CreateContestTypeDomain)

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[ContestTypeDomain]: #type: ignore
        return await super().get_all()
    
    async def filter(
        self,
        study_form_ids: Optional[List[int]] = None,
        education_level_ids: Optional[List[int]] = None,
    ) -> List[int]:
        stmt = (
            select(distinct(ContestType.id))
            .join(ContestType.contest_exams)
            .join(ProgramContestExam.program)
        )

        if study_form_ids:
            stmt = stmt.where(Program.study_form_id.in_(study_form_ids))
        if education_level_ids:
            stmt = stmt.where(Program.education_level_id.in_(education_level_ids))

        result = await self.db.execute(stmt)
        return [id for id in result.scalars().all()]
