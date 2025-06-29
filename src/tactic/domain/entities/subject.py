from typing import List, Optional

from pydantic import BaseModel


class SubjectDto(BaseModel):
    id: int
    name: str
    popularity: Optional[int]
    aliases: List["SubjectAliasDomain"]


class SubjectDomain(BaseModel):
    id: int
    name: str
    popularity: Optional[int]

class CreateSubjectDomain(BaseModel):
    name: str
    popularity: Optional[int]


class SubjectAliasDomain(BaseModel):
    id: int
    alias: str
    subject_id: int


class CreateSubjectAliasDomain(BaseModel):
    alias: str
    subject_id: int
