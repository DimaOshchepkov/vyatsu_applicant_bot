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
    
    
@pytest.mark.asyncio
async def test_get_many(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    c1 = await repo.add(CreateCategoryDomain(title="X", parent_id=None))
    c2 = await repo.add(CreateCategoryDomain(title="Y", parent_id=None))

    many = await repo.get_many([c1.id, c2.id])
    titles = {cat.title for cat in many}

    assert titles == {"X", "Y"}


@pytest.mark.asyncio
async def test_add_all(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    create_list = [
        CreateCategoryDomain(title="C1", parent_id=None),
        CreateCategoryDomain(title="C2", parent_id=None),
    ]

    added = await repo.add_all(create_list)
    assert len(added) == 2
    assert set(cat.title for cat in added) == {"C1", "C2"}


@pytest.mark.asyncio
async def test_update(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    created = await repo.add(CreateCategoryDomain(title="Old", parent_id=None))
    updated = CategoryDomain(id=created.id, title="New", parent_id=None)

    result = await repo.update(updated)
    assert result.title == "New"

    fetched = await repo.get(created.id)
    assert fetched and fetched.title == "New"


@pytest.mark.asyncio
async def test_delete(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    created = await repo.add(CreateCategoryDomain(title="ToDelete", parent_id=None))

    await repo.delete(created.id)
    assert await repo.get(created.id) is None


@pytest.mark.asyncio
async def test_delete_all(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )
    c1 = await repo.add(CreateCategoryDomain(title="Del1", parent_id=None))
    c2 = await repo.add(CreateCategoryDomain(title="Del2", parent_id=None))

    await repo.delete_all([c1.id, c2.id])
    result = await repo.get_many([c1.id, c2.id])
    assert result == []


@pytest.mark.asyncio
async def test_get_many_empty(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )

    result = await repo.get_many([])
    assert result == []
    
    
@pytest.mark.asyncio
async def test_delete_all_empty(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )

    await repo.delete_all([]) 
    
    
@pytest.mark.asyncio
async def test_get_non_existent(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )

    result = await repo.get(9999)
    assert result is None
    

@pytest.mark.asyncio
async def test_update_non_existent_creates(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )

    domain = CategoryDomain(id=999, title="Ghost", parent_id=None)
    result = await repo.update(domain)

    assert result.id == 999
    assert result.title == "Ghost"

    fetched = await repo.get(999)
    assert fetched is not None and fetched.title == "Ghost"
    
    
@pytest.mark.asyncio
async def test_add_all_empty(session_with_drop_after: AsyncSession):
    repo = BaseRepository[CategoryDomain, Category, CreateCategoryDomain](
        session_with_drop_after, CategoryDomain, Category, CreateCategoryDomain
    )

    result = await repo.add_all([])
    assert result == []