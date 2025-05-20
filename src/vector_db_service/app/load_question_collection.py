import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from vector_db_service.app.embedding_model import sentence_model
from vector_db_service.app.repositories.question_repository import QuestionRepository
from vector_db_service.app.settings import db_settings, qdrant_settings

logger = logging.getLogger(__name__)


async def recreate_collection_from_repository():
    client = QdrantClient(
        host=qdrant_settings.qdrant_host_name,
        port=qdrant_settings.qdrant_port,
    )

    collection_name = qdrant_settings.qdrant_question_collection

    # Удаляем старую коллекцию
    existing = client.get_collections().collections
    if collection_name in [c.name for c in existing]:
        logger.info(f"Удаляем старую коллекцию {collection_name}")
        client.delete_collection(collection_name=collection_name)

    logger.info(f"Создание коллекции {collection_name}")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=qdrant_settings.embedded_size, distance=Distance.COSINE
        ),
    )

    batch_size = 100
    offset = 0
    vector_id = 0

    engine = create_async_engine(
        db_settings.get_connection_url(),
        future=True,
    )

    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with session_factory() as session:
        repo = QuestionRepository(session)
        all_loaded = False

        while not all_loaded:
            items, total = await repo.get_questions_with_path(
                offset=offset, limit=batch_size
            )
            if not items:
                break

            points = []
            for item in items:
                combined_text = f"{' > '.join(item.path)} — {item.question}"
                vector = sentence_model.encode(combined_text)
                points.append(
                    PointStruct(id=vector_id, vector=vector, payload=item.model_dump())
                )
                vector_id += 1

            client.upsert(collection_name=collection_name, points=points)
            logger.info(f"Загружено {offset + len(items)} / {total}")

            offset += batch_size
            if offset >= total:
                all_loaded = True

    logger.info("Коллекция успешно создана и заполнена.")


async def load_question_collection():
    await recreate_collection_from_repository()
