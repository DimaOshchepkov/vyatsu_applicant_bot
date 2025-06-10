from pydantic import BaseModel
from datetime import datetime, date


class TimelineEventDomain(BaseModel):

    id: int
    binding_id: int
    name_id: int
    deadline: date
    

class TimelineEventDTO(BaseModel):
    id: int
    name_id: int
    event_name: str
    deadline: datetime


