from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import Program, ProgramTimelineBinding, TimelineEvent
from tactic.application.common.repositories import TimelineEventRepository
from tactic.domain.entities.timeline_event import TimelineEventDomain, TimelineEventDTO
from tactic.infrastructure.repositories.base_repository import BaseRepository


class TimelineEventRepositoryImpl(
    BaseRepository[TimelineEventDomain, TimelineEvent], TimelineEventRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, TimelineEventDomain, TimelineEvent)

    async def filter(
        self, program_id: int | None, timeline_type_id: int | None
    ) -> List[TimelineEventDTO]:
        if program_id is None and timeline_type_id is None:
            return []

        stmt = (
            select(TimelineEvent)
            .join(
                ProgramTimelineBinding,
                TimelineEvent.binding_id == ProgramTimelineBinding.id,
            )
            .join(
                Program,
                (
                    Program.education_level_id
                    == ProgramTimelineBinding.education_level_id
                )
                & (Program.study_form_id == ProgramTimelineBinding.study_form_id),
            )
            .options(selectinload(TimelineEvent.event_name))
            .order_by(TimelineEvent.deadline)
        )

        if timeline_type_id is not None:
            stmt = stmt.where(ProgramTimelineBinding.type_id == timeline_type_id)

        if program_id is not None:
            stmt = stmt.where(Program.id == program_id)

        result = await self.db.execute(stmt)
        orm_objects = result.scalars().all()
        return [self.to_dto(obj) for obj in orm_objects]

    def to_dto(self, orm: TimelineEvent):
        return TimelineEventDTO(
            id=orm.id,
            name_id=orm.name_id,
            event_name=orm.event_name.name,
            deadline=orm.deadline,
        )
