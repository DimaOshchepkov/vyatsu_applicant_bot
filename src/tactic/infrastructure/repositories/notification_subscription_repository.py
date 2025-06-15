from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import NotificationSubscription
from tactic.application.common.repositories import NotificationSubscriptionRepository
from tactic.domain.entities.notification_subscription import (
    CreateNotificationSubscriptionDomain,
    NotificationSubscriptionDomain,
)
from tactic.infrastructure.repositories.base_repository import BaseRepository


class NotificationSubscriptionRepositoryImpl(
    BaseRepository[
        NotificationSubscriptionDomain,
        NotificationSubscription,
        CreateNotificationSubscriptionDomain,
    ],
    NotificationSubscriptionRepository,
):

    def __init__(self, db: AsyncSession):
        super().__init__(
            db,
            NotificationSubscriptionDomain,
            NotificationSubscription,
            CreateNotificationSubscriptionDomain,
        )

    async def filter(
        self,
        user_id: Optional[int] = None,
        program_id: Optional[int] = None,
        timeline_type_id: Optional[int] = None,
    ) -> List[NotificationSubscriptionDomain]:
        stmt = select(self.orm_model)

        # Условия фильтрации
        if user_id is not None:
            stmt = stmt.where(self.orm_model.user_id == user_id)
        if program_id is not None:
            stmt = stmt.where(self.orm_model.program_id == program_id)
        if timeline_type_id is not None:
            stmt = stmt.where(self.orm_model.timeline_type_id == timeline_type_id)

        result = await self.db.execute(stmt)
        objs = result.scalars().all()
        return [self.to_domain(obj) for obj in objs]
