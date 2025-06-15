from __future__ import annotations
from pydantic import BaseModel
from typing import List


class CategoryNodeModel(BaseModel):
    id: int
    title: str
    children: List[CategoryNodeModel] = []
    
class CreateCategoryNodeModel(BaseModel):
    title: str
    children: List[CategoryNodeModel] = []
