from enum import IntEnum
from pydantic import BaseModel


class EducationLevelDomain(BaseModel):
    id: int
    name: str
    
class EducationLevelEnum(IntEnum):
    MASTER = 1
    BACHELOR = 2
    COLLEGE = 3
    PHD = 4
    

class CreateEducationLevelDomain(BaseModel):
    name: str

