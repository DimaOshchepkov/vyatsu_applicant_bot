from typing import List

from aiocache import cached
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Category
from tactic.application.common.repositories import CategoryRepository
from tactic.domain.entities.category import CategoryDomain, CreateCategoryDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class CategoryRepositoryImpl(
    BaseRepository[CategoryDomain, Category, CreateCategoryDomain], CategoryRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CategoryDomain, Category, CreateCategoryDomain)

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[CategoryDomain]: # type: ignore
        return await super().get_all()

