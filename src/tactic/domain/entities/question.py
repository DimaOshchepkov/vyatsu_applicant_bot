from typing import Optional
from pydantic import BaseModel


class QuestionDomain(BaseModel):

    id: int 
    question: str
    answer: Optional[str]
    category_id: int
