from typing import List

from pydantic import BaseModel


class ProgramResponseEntry(BaseModel):
    program_id: int
    title: str
    url: str
    score: float


class SearchRequestDTO(BaseModel):
    query: str
    k: int
    programs_id: List[int]
