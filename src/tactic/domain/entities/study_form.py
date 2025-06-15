from pydantic import BaseModel


class StudyFormDomain(BaseModel):
    id: int
    name: str
    
class CreateStudyFormDomain(BaseModel):
    name: str
