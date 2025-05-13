from typing import Optional
from pydantic import BaseModel


class CategoryDomain(BaseModel):
    id: int
    title: str
    parent_id: Optional[int]
