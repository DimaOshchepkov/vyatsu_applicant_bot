import asyncio
import json
import os

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.models import Category, Question
from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_async_sessionmaker, get_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "merged_questions.json")


async def get_or_create_category(session: AsyncSession, path: list[str]) -> Category:
    parent = None
    for title in path:
        stmt = select(Category).where(
            Category.title == title, Category.parent == parent
        )
        result = await session.execute(stmt)
        category = result.scalars().first()

        if not category:
            category = Category(title=title, parent=parent)
            session.add(category)
            await session.flush()  # Нужен для получения ID
        parent = category
    return parent


async def load_data_from_file(file_path: str, session: AsyncSession):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        for item in data:
            category = await get_or_create_category(session, item["path"])
            question = Question(
                question=item["question"], answer=item.get("answer"), category=category
            )
            session.add(question)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise
    finally:
        await session.close()


async def load(session_factory: async_sessionmaker[AsyncSession]):

    async with session_factory() as session:
        try:
            # Очистка таблиц
            await session.execute(delete(Question))
            await session.execute(delete(Category))
            await session.commit()

            # Загрузка данных
            await load_data_from_file(json_path, session=session)

        except Exception as e:
            await session.rollback()
            raise


async def main():
    config = load_config()

    engine_factory = get_engine(config.db)
    engine = await anext(engine_factory)
    session_factory = await get_async_sessionmaker(engine)
    
    await load(session_factory)



if __name__ == "__main__":
    asyncio.run(main())
