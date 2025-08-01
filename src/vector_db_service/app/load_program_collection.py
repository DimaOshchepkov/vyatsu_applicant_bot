import logging
from typing import List, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from shared.models import Program
from vector_db_service.app.embedding_model import embedder
from vector_db_service.app.repositories.program_repository import ProgramRepository
from vector_db_service.app.settings import db_settings, qdrant_settings

qdrant = QdrantClient(
    host=qdrant_settings.qdrant_host_name, port=qdrant_settings.qdrant_port
)


def program_to_text(program: Program) -> str:
    return f"{program.program_info or ''} {program.career_info or ''}"


def to_point(program: Program, vector: List[float]) -> PointStruct:
    return PointStruct(
        id=program.id,
        vector=vector,
        payload={
            "title": program.title,
            "url": program.url,
            "program_id": program.id,
        },
    )


async def upload_program_vectors(programs: Sequence[Program]):
    if not programs:
        return

    await create_collection_if_needed()

    combined_texts = [program_to_text(program) for program in programs]
    vectors = embedder.encode_batch(combined_texts)

    points = [to_point(p, v) for p, v in zip(programs, vectors)]
    qdrant.upsert(
        collection_name=qdrant_settings.qdrant_program_collection, points=points
    )


async def create_collection_if_needed():
    collections = qdrant.get_collections().collections
    if qdrant_settings.qdrant_program_collection not in [c.name for c in collections]:
        qdrant.recreate_collection(
            collection_name=qdrant_settings.qdrant_program_collection,
            vectors_config=VectorParams(
                size=qdrant_settings.embedded_size, distance=Distance.COSINE
            ),
        )


async def load_program_collection():
    engine = create_async_engine(
        db_settings.get_connection_url(),
        future=True,
    )

    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_factory() as session:
        repo = ProgramRepository(session)
        offset = 0
        batch_size = 100

        while True:
            programs, total = await repo.get_paginated(limit=batch_size, offset=offset)
            if not programs:
                break

            await upload_program_vectors(programs)
            offset += batch_size
