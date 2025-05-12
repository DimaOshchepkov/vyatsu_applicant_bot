import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


from tactic.infrastructure.db.models import Base, Category
from tactic.infrastructure.repositories.category_repository import CategoryRepositoryImpl
from tests.settings import settings



DATABASE_URL = settings.get_connection_url()


engine = create_async_engine(DATABASE_URL, echo=False)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def seeded_categories(db_session):
    root = Category(id=1, title="Root")
    child = Category(id=2, title="Child", parent_id=1)
    db_session.add_all([root, child])
    await db_session.commit()
    return [root, child]

async def test_get_all_categories(db_session: AsyncSession, seeded_categories):
    repo = CategoryRepositoryImpl(db_session)
    category_root = (await repo.get_category_tree())[0]


    assert "Root" in category_root.title
    assert "Child" in category_root.children[0].title
    assert len(category_root.children[0].children) == 0