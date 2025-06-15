from pydantic import BaseModel


class NotificationSubscriptionDomain(BaseModel):
    id: int
    user_id: int
    program_id: int
    timeline_type_id: int
    
class NotificationSubscriptionDTO(BaseModel):
    id: int
    program_title: str
    timeline_type_name: str
    
class CreateNotificationSubscriptionDomain(BaseModel):
    user_id: int
    program_id: int
    timeline_type_id: int