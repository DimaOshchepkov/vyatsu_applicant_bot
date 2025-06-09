from typing import List

from tactic.application.common.repositories import TimelineEventRepository
from tactic.domain.entities.timeline_event import TimelineEventDTO


class GetTimelineEventUseCase:

    def __init__(self, timeline_repository: TimelineEventRepository):
        self.timeline_repository = timeline_repository

    async def __call__(
        self, program_id: int, timeline_type_id: int
    ) -> List[TimelineEventDTO]:
        return await self.timeline_repository.filter(program_id, timeline_type_id)
