from typing import List
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    path: List[str] = []
    k: int = 3


class ResponseEntry(BaseModel):
    question: str
    answer: str
    path: List[str]
    score: float


class VectorSearchResponse(BaseModel):
    results: List[ResponseEntry]
