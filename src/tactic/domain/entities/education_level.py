from pydantic import BaseModel


class EducationLevelDomain(BaseModel):
    id: int
    name: str

