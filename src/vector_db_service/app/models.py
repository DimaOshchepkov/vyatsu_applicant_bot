from typing import List

from pydantic import BaseModel


class ResponseEntry(BaseModel):
    question: str
    answer: str
    path: List[str]
    score: float


class VectorSearchResponse(BaseModel):
    results: List[ResponseEntry]
    
    
class QuestionItem(BaseModel):
    question: str
    path: List[str]
    answer: str
