from typing import List

from tactic.application.common.repositories import (
    NotificationSubscriptionRepository,
    ProgramRepository,
    TimelineTypeRepository,
)
from tactic.domain.entities.notification_subscription import NotificationSubscriptionDTO


class GetListSubscriptionsUseCase:
    def __init__(
        self,
        subscription_repo: NotificationSubscriptionRepository,
        program_repo: ProgramRepository,
        timeline_type_repo: TimelineTypeRepository,
    ):
        self.subscription_repo = subscription_repo
        self.program_repo = program_repo
        self.timeline_type_repo = timeline_type_repo

    async def __call__(self, user_id: int) -> List[NotificationSubscriptionDTO]:
        subscriptions_domain = await self.subscription_repo.filter(user_id=user_id)

        program_ids = {sub.program_id for sub in subscriptions_domain}
        timeline_type_ids = {sub.timeline_type_id for sub in subscriptions_domain}

        programs = await self.program_repo.get_many(program_ids)
        timeline_types = await self.timeline_type_repo.get_many(timeline_type_ids)

        program_map = {p.id: p for p in programs}
        timeline_type_map = {t.id: t for t in timeline_types}

        subscriptions_dto = []
        for sub in subscriptions_domain:
            program = program_map.get(sub.program_id)
            timeline_type = timeline_type_map.get(sub.timeline_type_id)
            if program and timeline_type:
                subscriptions_dto.append(
                    NotificationSubscriptionDTO(
                        id=sub.id,
                        program_title=program.title,
                        timeline_type_name=timeline_type.name,
                    )
                )

        return subscriptions_dto
