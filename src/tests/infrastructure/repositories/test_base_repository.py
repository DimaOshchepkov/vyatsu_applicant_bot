# test_base_repository.py
import pytest

from tactic.domain.entities.category import CategoryDomain
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import Category
from tactic.infrastructure.repositories.base_repository import BaseRepository


@pytest.mark.asyncio
async def test_add_and_get(db_session: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category](db_session, CategoryDomain, Category)
    category_domain = CategoryDomain(id=1, title="Alice", parent_id=None)

    added = await repo.add(category_domain)
    assert added == category_domain

    fetched = await repo.get(1)
    assert fetched == category_domain


@pytest.mark.asyncio
async def test_get_all(db_session: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category](db_session, CategoryDomain, Category)
    await repo.add(CategoryDomain(id=1, title="A", parent_id=None))
    await repo.add(CategoryDomain(id=2, title="B", parent_id=None))

    all_categories = await repo.get_all()
    assert len(all_categories) == 2
    assert all(category.id in [1, 2] for category in all_categories)
