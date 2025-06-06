import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Category
from tactic.infrastructure.repositories.category_repository import (
    CategoryRepositoryImpl,
)


@pytest.fixture
async def seeded_categories(db_session: AsyncSession):
    root = Category(title="Root")
    db_session.add(root)
    await db_session.flush()

    child = Category(title="Child", parent_id=root.id)
    db_session.add(child)
    await db_session.flush()

    return db_session, [root, child]


@pytest.mark.asyncio
async def test_get_category_tree(seeded_categories):

    db_session, [root, child] = seeded_categories
    repo = CategoryRepositoryImpl(db_session)
    category_root = (await repo.get_category_tree())[0]

    assert "Root" in category_root.title
    assert "Child" in category_root.children[0].title
    assert len(category_root.children[0].children) == 0
