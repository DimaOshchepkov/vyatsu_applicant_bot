from datetime import date, datetime

from pydantic import BaseModel


class ScheduledNotificationDomain(BaseModel):
    id: int
    subscription_id: int
    event_id: int
    send_at: datetime
    
class ScheduledNotificationDTO(BaseModel):
    id: int
    event_name: str
    send_at: datetime
    deadline: date
    
class CreateScheduledNotificationDomain(BaseModel):
    subscription_id: int
    event_id: int
    send_at: datetime
