from typing import List

from pydantic import BaseModel

class Exam(BaseModel):
    exam: str
    aliases: List[str]
    popularity: int