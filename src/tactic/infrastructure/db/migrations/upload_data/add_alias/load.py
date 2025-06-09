import asyncio
import json
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from shared.models import Subject, SubjectAlias
from tactic.settings import db_settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "exam_aliase.json")


async def add_subjects_from_list(session: AsyncSession, data: list[dict]):
    for subject_data in data:
        result = await session.execute(
            select(Subject).where(Subject.name == subject_data["exam"])
        )
        subject = result.scalar_one_or_none()
        if subject is None:
            continue

        subject.popularity = subject_data["popularity"]
        session.add(subject)

        for alias in subject_data.get("aliases", []):
            session.add(SubjectAlias(alias=alias, subject_id=subject.id))
            await session.flush()

    await session.commit()


async def main():
    engine = create_async_engine(
        db_settings.get_connection_url(),
        future=True,
    )
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with session_factory() as session:
        await add_subjects_from_list(session, data)


if __name__ == "__main__":
    asyncio.run(main())
