from typing import List

from aiocache import cached
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import ContestType
from tactic.application.common.repositories import ContestTypeRepository
from tactic.domain.entities.contest_type import ContestTypeDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class ContestTypeRepositoryImpl(
    BaseRepository[ContestTypeDomain, ContestType], ContestTypeRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContestTypeDomain, ContestType)

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[ContestTypeDomain]:
        return await super().get_all()
