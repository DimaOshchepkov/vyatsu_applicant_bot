import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Category
from tactic.domain.entities.category import CategoryDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository


@pytest.mark.asyncio
async def test_add_and_get(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category](
        session_with_drop_after, CategoryDomain, Category
    )
    category_domain = CategoryDomain(id=1, title="Alice", parent_id=None)

    added = await repo.add(category_domain)
    assert added == category_domain

    fetched = await repo.get(1)
    assert fetched == category_domain


@pytest.mark.asyncio
async def test_get_all(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category](
        session_with_drop_after, CategoryDomain, Category
    )
    await repo.add(CategoryDomain(id=1, title="A", parent_id=None))
    await repo.add(CategoryDomain(id=2, title="B", parent_id=None))

    all_categories = await repo.get_all()
    assert len(all_categories) == 2
    assert all(category.id in [1, 2] for category in all_categories)
