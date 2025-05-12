from typing import List

from sqlalchemy import select

from tactic.application.common.repositories import CategoryRepository
from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.infrastructure.db.models import Category
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryRepositoryImpl(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_category_tree(self) -> List[CategoryNodeModel]:
        stmt = select(Category)
        result = await self.session.execute(stmt)
        categories = result.scalars().all()

        # Промежуточное хранилище для узлов
        category_map: dict[int, CategoryNodeModel] = {}

        # Сначала создаём узлы без детей
        for category in categories:
            category_map[category.id] = CategoryNodeModel(
                id=category.id,
                title=category.title,
                children=[]
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
