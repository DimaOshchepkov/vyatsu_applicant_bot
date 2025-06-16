from pydantic import BaseModel


class TimelineEventNameDomain(BaseModel):
    id: int
    name: str
    
class CreateTimelineEventNameDomain(BaseModel):
    name: str
    
    
    