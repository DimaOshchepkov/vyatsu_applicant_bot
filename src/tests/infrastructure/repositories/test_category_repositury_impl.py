import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tactic.infrastructure.db.models import  Category
from tactic.infrastructure.repositories.category_repository import CategoryRepositoryImpl



@pytest.fixture
async def seeded_categories(db_session):
    root = Category(id=1, title="Root")
    child = Category(id=2, title="Child", parent_id=1)
    db_session.add_all([root, child])
    await db_session.commit()
    return [root, child]


async def test_get_category_tree(db_session: AsyncSession, seeded_categories):
    repo = CategoryRepositoryImpl(db_session)
    category_root = (await repo.get_category_tree())[0]


    assert "Root" in category_root.title
    assert "Child" in category_root.children[0].title
    assert len(category_root.children[0].children) == 0