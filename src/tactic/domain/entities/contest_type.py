from pydantic import BaseModel


class ContestTypeDomain(BaseModel):
    id: int
    name: str
    
class CreateContestTypeDomain(BaseModel):
    name: str