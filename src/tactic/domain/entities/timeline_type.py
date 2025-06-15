from enum import IntEnum

from pydantic import BaseModel


class PaymentType(IntEnum):
    PAID = 1
    BUDGET = 2

class TimelineTypeDomain(BaseModel):
    id: int
    name: str

class CreateTimelineTypeDomain(BaseModel):
    name: str
