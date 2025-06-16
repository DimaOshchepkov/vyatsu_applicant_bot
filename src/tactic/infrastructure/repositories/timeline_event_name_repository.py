from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import TimelineEventName
from tactic.application.common.repositories import TimelineEventNameRepository
from tactic.domain.entities.timeline_event_name import (
    CreateTimelineEventNameDomain,
    TimelineEventNameDomain,
)
from tactic.infrastructure.repositories.base_repository import BaseRepository


class TimelineEventNameRepositoryImpl(
    BaseRepository[
        TimelineEventNameDomain, TimelineEventName, CreateTimelineEventNameDomain
    ],
    TimelineEventNameRepository,
):
    def __init__(self, db: AsyncSession):
        super().__init__(
            db,
            TimelineEventNameDomain,
            TimelineEventName,
            CreateTimelineEventNameDomain,
        )
