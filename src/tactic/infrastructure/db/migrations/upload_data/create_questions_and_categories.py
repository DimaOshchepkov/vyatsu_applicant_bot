import asyncio
import json


from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_async_sessionmaker, get_engine
from shared.models import Category, Question
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_or_create_category(session: AsyncSession, path: list[str]) -> Category:
    parent = None
    for title in path:
        stmt = select(Category).where(Category.title == title, Category.parent == parent)
        result = await session.execute(stmt)
        category = result.scalars().first()

        if not category:
            category = Category(title=title, parent=parent)
            session.add(category)
            await session.flush()  # Нужен для получения ID
        parent = category
    return parent

async def load_data_from_file(file_path: str, session: AsyncSession):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        for item in data:
            category = await get_or_create_category(session, item['path'])
            question = Question(
                question=item['question'],
                answer=item.get('answer'),
                category=category
            )
            session.add(question)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise
    finally:
        await session.close()
        
async def main(): 
    config = load_config()

    engine_factory = get_engine(config.db)
    engine = await anext(engine_factory)

    session_factory = await get_async_sessionmaker(engine)
    async with session_factory() as session:
        await load_data_from_file('merged_questions.json', session=session)
        
if __name__ == '__main__':
    asyncio.run(main())
