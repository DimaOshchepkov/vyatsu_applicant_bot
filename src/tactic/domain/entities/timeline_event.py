from pydantic import BaseModel
from sqlalchemy import Date


class TimelineEventDomain(BaseModel):

    id: int
    binding_id: int
    name_id: int
    deadline: Date
    

class TimelineEventDTO(BaseModel):
    id: int
    name_id: int
    event_name: str
    deadline: Date


