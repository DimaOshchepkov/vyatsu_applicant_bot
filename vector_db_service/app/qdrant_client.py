from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, MatchValue, FieldCondition
from .models import VectorSearchResponse, ResponseEntry
from .get_config import settings
from .embedding_model import sentence_model, SentenceEmbedder

client = QdrantClient(host=settings.qdrant_host_name, port=settings.qdrant_port)  

COLLECTION_NAME = settings.collection_name

embedder = SentenceEmbedder(sentence_model)


def make_path_filter(path: List[str]) -> Filter:
    return Filter(
        must=[
            FieldCondition(
                key="path",
                match=MatchValue(value=segment)
            ) for segment in path
        ]
    )
 
    
async def search_similar_question(
    user_query: str,
    path: Optional[List[str]] = None,
    k: int = 5
) -> VectorSearchResponse:
    
    vector = embedder.encode(user_query)
    query_filter: Optional[Filter] = make_path_filter(path) if path else None

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=query_filter,
        limit=k
    )

    results: List[ResponseEntry] = []
    for hit in hits.points:
        payload = hit.payload or {}
        results.append(
            ResponseEntry(
                question=payload.get("question", ""),
                answer=payload.get("answer", ""),
                path=payload.get("path") or [],
                score=hit.score
            )
        )

    return VectorSearchResponse(results=results)