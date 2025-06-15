from typing import List, Optional

from pydantic import BaseModel


class SubjectJsonDomain(BaseModel):
    exam: str
    aliases: List[str]
    popularity: int


class SubjectDomain(BaseModel):
    id: int
    name: str
    popularity: Optional[int]
    aliases: List["SubjectAliasDomain"]


class CreateSubjectDomain(BaseModel):
    name: str
    popularity: Optional[int]
    aliases: List["SubjectAliasDomain"]


class SubjectAliasDomain(BaseModel):
    id: int
    alias: str
    subject_id: int


class CreateSubjectAliasDomain(BaseModel):
    id: int
    alias: str
    subject_id: int
