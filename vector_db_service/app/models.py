from pydantic import BaseModel
from typing import List, Dict, Any


class ResponseEntry(BaseModel):
    question: str
    answer: str
    path: List[str]
    score: float
    

class VectorSearchResponse(BaseModel):
    results: List[ResponseEntry]
