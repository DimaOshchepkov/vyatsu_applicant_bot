import asyncio
import logging
import subprocess
import sys

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shared.models import Category, Program, SubjectAlias
from tactic.infrastructure.db.migrations.upload_data.add_alias.load import (
    load as add_alias,
)
from tactic.infrastructure.db.migrations.upload_data.create_question_and_categories.load import (
    load as load_questions,
)
from tactic.infrastructure.db.migrations.upload_data.education_areas.load import (
    load as load_areas,
)
from tactic.infrastructure.db.migrations.upload_data.table_exist_and_empty import table_exists_and_empty
from tactic.settings import db_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()  # корневой логгер


def run_migrations():
    logger.info("🚀 Выполняем миграции Alembic...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("✅ Миграции выполнены успешно.")
    except subprocess.CalledProcessError as e:
        logger.error("❌ Ошибка при выполнении миграций: %s", e)
        sys.exit(1)





async def run_async_checks():
    engine = create_async_engine(
        db_settings.get_connection_url(),
        future=True,
    )
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    if await table_exists_and_empty(engine, Category):
        logger.info(
            f"Таблица '{Category.__tablename__}' пуста — запускаем инициализацию."
        )
        await load_questions(session_factory)

    if await table_exists_and_empty(engine, Program):
        logger.info(
            f"Таблица '{Program.__tablename__}' пуста — запускаем инициализацию."
        )
        await load_areas(session_factory)

    if await table_exists_and_empty(engine, SubjectAlias):
        logger.info(
            f"Таблица '{SubjectAlias.__tablename__}' пуста — запускаем инициализацию."
        )
        await add_alias(session_factory)



def main():
    run_migrations()
    asyncio.run(run_async_checks())


if __name__ == "__main__":
    main()
