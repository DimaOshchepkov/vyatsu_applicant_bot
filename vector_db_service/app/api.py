from fastapi import APIRouter
from app.qdrant_client import search_similar_question
from app.models import VectorSearchResponse

router = APIRouter()


@router.post("/search", response_model=VectorSearchResponse)
async def search(query: str):
    return await search_similar_question(query)


@router.get("/health")
async def health():
    return {"status": "ok"}