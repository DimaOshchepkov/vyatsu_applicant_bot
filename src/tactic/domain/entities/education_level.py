from pydantic import BaseModel


class EducationLevelDomain(BaseModel):
    id: int
    name: str
    
class CreateEducationLevelDomain(BaseModel):
    name: str

