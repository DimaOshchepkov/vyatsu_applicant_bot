import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Category
from tactic.domain.entities.category import CategoryDomain, CreateCategoryDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository


@pytest.mark.asyncio
async def test_add_and_get(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    category_domain = CreateCategoryDomain(title="Alice", parent_id=None)

    added = await repo.add(category_domain)
    assert added.title == category_domain.title

    fetched = await repo.get(1)
    assert fetched.title if fetched else '' == category_domain.title


@pytest.mark.asyncio
async def test_get_all(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    await repo.add(CreateCategoryDomain(title="A", parent_id=None))
    await repo.add(CreateCategoryDomain(title="B", parent_id=None))

    all_categories = await repo.get_all()
    assert len(all_categories) == 2
    assert all(category.title in ["A", "B"] for category in all_categories)
