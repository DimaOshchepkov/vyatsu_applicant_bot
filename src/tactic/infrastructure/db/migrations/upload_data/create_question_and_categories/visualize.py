import asyncio
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from shared.models import Category, Question
from tactic.infrastructure.config_loader import load_config
from tactic.infrastructure.db.main import get_async_sessionmaker, get_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_to_file = os.path.join(BASE_DIR, "tree.txt")


async def build_tree(session: AsyncSession):
    result = await session.execute(
        select(Category).options(selectinload(Category.children))
    )
    all_categories = result.scalars().all()

    # Корневые — те, у кого нет родителя
    roots = [cat for cat in all_categories if cat.parent_id is None]
    return roots


def draw_tree(categories: list[Category], prefix: str = "") -> str:
    lines = []
    count = len(categories)
    for i, cat in enumerate(categories):
        connector = "└── " if i == count - 1 else "├── "
        lines.append(f"{prefix}{connector}{cat.title}")

        # Углубляем отступ
        extension = "    " if i == count - 1 else "│   "
        child_lines = draw_tree(cat.children, prefix + extension)
        if child_lines:
            lines.append(child_lines)
    return "\n".join(lines)


async def load(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        try:
            tree = await build_tree(session)
            tree_text = draw_tree(tree)

            path = Path(path_to_file)
            path.write_text(tree_text, encoding="utf-8")

            print(f"Дерево категорий записано в {path.resolve()}")
        except Exception as e:
            raise


async def main():
    config = load_config()

    engine_factory = get_engine(config.db)
    engine = await anext(engine_factory)
    session_factory = await get_async_sessionmaker(engine)

    await load(session_factory)


if __name__ == "__main__":
    asyncio.run(main())
