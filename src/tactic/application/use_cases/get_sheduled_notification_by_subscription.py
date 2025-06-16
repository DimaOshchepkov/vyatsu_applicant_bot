from typing import List

from tactic.application.common.repositories import (
    ScheduledNotificationRepository,
    TimelineEventNameRepository,
    TimelineEventRepository,
)
from tactic.domain.entities.sheduled_notification import ScheduledNotificationDTO


class GetScheduledNotificationsBySubscriptionUseCase:
    def __init__(
        self,
        notification_repo: ScheduledNotificationRepository,
        event_repo: TimelineEventRepository,
        name_repo: TimelineEventNameRepository,
    ):
        self.notification_repo = notification_repo
        self.event_repo = event_repo
        self.name_repo = name_repo

    async def __call__(self, subscription_id: int) -> List[ScheduledNotificationDTO]:
        # Получаем уведомления
        notifications = await self.notification_repo.filter(subscription_id)
        if not notifications:
            return []

        # Получаем все event_id → TimelineEvent
        event_ids = [n.event_id for n in notifications]
        events = await self.event_repo.get_many(event_ids)
        event_map = {e.id: e for e in events}

        # Получаем все name_id → TimelineEventName
        name_ids = list({event.name_id for event in events})
        names = await self.name_repo.get_many(name_ids)
        name_map = {n.id: n.name for n in names}

        # Собираем результат
        result: List[ScheduledNotificationDTO] = []

        for notification in notifications:
            event = event_map.get(notification.event_id)
            if not event:
                continue

            event_name = name_map.get(event.name_id, "Неизвестное событие")

            dto = ScheduledNotificationDTO(
                id=notification.id,
                event_name=event_name,
                send_at=notification.send_at,
            )
            result.append(dto)

        return result
