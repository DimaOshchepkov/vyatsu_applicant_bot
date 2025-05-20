from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, HasIdCondition, MatchValue

from vector_db_service.app.embedding_model import embedder
from vector_db_service.app.models import (
    ProgramResponseEntry,
    ResponseEntry,
    VectorSearchResponse,
)
from vector_db_service.app.settings import qdrant_settings

client = QdrantClient(
    host=qdrant_settings.qdrant_host_name, port=qdrant_settings.qdrant_port
)


def make_path_filter(path: List[str]) -> Filter:
    return Filter(
        must=[
            FieldCondition(key="path", match=MatchValue(value=segment))
            for segment in path
        ]
    )


async def search_similar_question(
    user_query: str, path: List[str] = [], k: int = 5
) -> VectorSearchResponse:

    vector = embedder.encode(user_query)
    query_filter: Optional[Filter] = make_path_filter(path) if len(path) != 0 else None

    hits = client.query_points(
        collection_name=qdrant_settings.qdrant_question_collection,
        query=vector,
        query_filter=query_filter,
        limit=k,
    )

    results: List[ResponseEntry] = []
    for hit in hits.points:
        payload = hit.payload or {}
        results.append(
            ResponseEntry(
                question=payload.get("question", ""),
                answer=payload.get("answer", ""),
                path=payload.get("path") or [],
                score=hit.score,
            )
        )

    return VectorSearchResponse(results=results)


async def search_similar_program_ids(
    text: str, top_k: int = 5, allowed_ids: List[int] = []
) -> List[ProgramResponseEntry]:
    vector = embedder.encode(text)

    filter = (
        Filter(must=HasIdCondition(has_id=[x for x in allowed_ids]))
        if len(allowed_ids) != 0
        else None
    )

    hits = client.query_points(
        collection_name=qdrant_settings.qdrant_program_collection,
        query=vector,
        query_filter=filter,
        limit=top_k,
    )

    results: List[ProgramResponseEntry] = []
    for hit in hits.points:
        payload = hit.payload or {}
        results.append(
            ProgramResponseEntry(
                program_id=int(hit.id),
                title=payload.get("title", ""),
                url=payload.get("url", ""),
                score=hit.score,
            )
        )

    return results
