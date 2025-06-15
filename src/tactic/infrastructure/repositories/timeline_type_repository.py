
from shared.models import TimelineType
from tactic.application.common.repositories import TimelineTypeRepository
from tactic.domain.entities.timeline_type import CreateTimelineTypeDomain, TimelineTypeDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TimelineTypeRepositoryImpl(
    BaseRepository[TimelineTypeDomain, TimelineType, CreateTimelineTypeDomain],
    TimelineTypeRepository,
):
    def __init__(self, db: AsyncSession):
        super().__init__(
            db, TimelineTypeDomain, TimelineType, CreateTimelineTypeDomain
        )