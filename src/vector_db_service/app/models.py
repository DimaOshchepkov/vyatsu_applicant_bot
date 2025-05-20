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


class SearchRequest(BaseModel):
    query: str
    path: List[str] = []
    k: int = 3
    
    
class ProgramRequest(BaseModel):
    query: str
    exams: List[int] = []
    k: int = 3
    
    
class ProgramResponseEntry(BaseModel):
    program_id: int
    title: str
    url: str
    score: float
    
    
    
