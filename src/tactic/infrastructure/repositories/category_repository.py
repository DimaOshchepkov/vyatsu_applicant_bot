from typing import List, Type

from aiocache import cached
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Category
from tactic.application.common.repositories import CategoryRepository
from tactic.domain.entities.category import CategoryDomain
from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import (
    classaware_key_builder,
    setup_cache,
)

setup_cache()


class CategoryRepositoryImpl(
    BaseRepository[CategoryDomain, Category], CategoryRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CategoryDomain, Category)

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[CategoryDomain]:
        return await super(CategoryRepositoryImpl, self).get_all()

    async def get_category_tree(self) -> List[CategoryNodeModel]:
        stmt = select(Category)
        result = await self.db.execute(stmt)
        categories = result.scalars().all()

        # Промежуточное хранилище для узлов
        category_map: dict[int, CategoryNodeModel] = {}

        # Сначала создаём узлы без детей
        for category in categories:
            category_map[category.id] = CategoryNodeModel(
                id=category.id, title=category.title, children=[]
            )

        roots: List[CategoryNodeModel] = []

        # Заполняем структуру дерева
        for category in categories:
            node = category_map[category.id]
            if category.parent_id:
                parent = category_map[category.parent_id]
                parent.children.append(node)
            else:
                roots.append(node)

        return roots
