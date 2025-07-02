from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import ScheduledNotification
from tactic.application.common.repositories import ScheduledNotificationRepository
from tactic.domain.entities.sheduled_notification import (
    CreateScheduledNotificationDomain,
    ScheduledNotificationDomain,
)
from tactic.infrastructure.repositories.base_repository import BaseRepository


class ScheduledNotificationRepositoryImpl(
    BaseRepository[
        ScheduledNotificationDomain,
        ScheduledNotification,
        CreateScheduledNotificationDomain,
    ],
    ScheduledNotificationRepository,
):
    def __init__(self, db: AsyncSession):
        super().__init__(
            db,
            ScheduledNotificationDomain,
            ScheduledNotification,
            CreateScheduledNotificationDomain,
        )

    async def filter(
        self, notification_subscription_id: Optional[int] = None
    ) -> List[ScheduledNotificationDomain]:
        stmt = select(self.orm_model)
        if notification_subscription_id is not None:
            stmt = stmt.where(
                self.orm_model.subscription_id == notification_subscription_id
            )

        result = await self.db.execute(stmt)
        objs = result.scalars().all()
        return [self.to_domain(obj) for obj in objs]
