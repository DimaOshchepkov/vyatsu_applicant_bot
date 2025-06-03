from pydantic import BaseModel


class ContestTypeDomain(BaseModel):
    id: int
    name: str