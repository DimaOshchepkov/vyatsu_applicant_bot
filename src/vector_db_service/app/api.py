from typing import List, Set

from fastapi import APIRouter

from vector_db_service.app.models import (
    ProgramRequest,
    ProgramResponseEntry,
    SearchRequest,
    VectorSearchResponse,
)
from vector_db_service.app.qdrant_client import (
    search_similar_program_ids,
    search_similar_question,
)

router = APIRouter()


@router.post("/search", response_model=VectorSearchResponse)
async def search(request: SearchRequest):
    return await search_similar_question(request.query, request.path, request.k)


@router.post("/programs")
async def programs(request: ProgramRequest) -> List[ProgramResponseEntry]:
    return await search_similar_program_ids(
        request.query, request.k, request.programs_id
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
