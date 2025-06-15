from typing import List

from aiocache import cached
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import EducationLevel
from tactic.application.common.repositories import EducationLevelRepository
from tactic.domain.entities.education_level import CreateEducationLevelDomain, EducationLevelDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class EducationLevelRepositoryImpl(
    BaseRepository[EducationLevelDomain, EducationLevel, CreateEducationLevelDomain],
    EducationLevelRepository,
):
    def __init__(self, db: AsyncSession):
        super().__init__(
            db, EducationLevelDomain, EducationLevel, CreateEducationLevelDomain
        )

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[EducationLevelDomain]: #type: ignore
        return await super().get_all()
