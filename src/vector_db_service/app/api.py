from fastapi import APIRouter

from vector_db_service.app.models import SearchRequest, VectorSearchResponse
from vector_db_service.app.qdrant_client import search_similar_question

router = APIRouter()


@router.post("/search", response_model=VectorSearchResponse)
async def search(request: SearchRequest):
    return await search_similar_question(request.query, request.path, request.k)


@router.get("/health")
async def health():
    return {"status": "ok"}
