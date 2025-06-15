from datetime import date, datetime

from pydantic import BaseModel


class TimelineEventDomain(BaseModel):
    id: int
    binding_id: int
    name_id: int
    deadline: date
    
class CreateTimelineEventDomain(BaseModel):
    binding_id: int
    name_id: int
    deadline: date


class TimelineEventDTO(BaseModel):
    id: int
    name_id: int
    event_name: str
    deadline: datetime
    
    
class SendEvent(BaseModel):
    id: int
    message: str
    when: datetime
