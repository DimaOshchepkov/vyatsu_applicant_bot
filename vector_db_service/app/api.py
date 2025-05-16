from typing import List, Optional
from fastapi import APIRouter
from app.qdrant_client import search_similar_question
from app.models import VectorSearchResponse


router = APIRouter()


@router.post("/search", response_model=VectorSearchResponse)
async def search(query: str, path: Optional[List[str]] = None, k: int = 3):
    return await search_similar_question(query, path, k)


@router.get("/health")
async def health():
    return {"status": "ok"}