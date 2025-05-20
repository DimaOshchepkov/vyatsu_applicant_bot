from typing import List

from pydantic import BaseModel


class ExamJsonDomain(BaseModel):
    exam: str
    aliases: List[str]
    popularity: int
    
    
class ExamDomain(BaseModel):
    id: int
    name: str
