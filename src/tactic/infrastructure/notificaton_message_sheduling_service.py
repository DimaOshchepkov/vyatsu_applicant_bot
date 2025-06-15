import asyncio
import logging
import traceback
from datetime import datetime, timedelta

from tactic.application.common.repositories import (
    NotificationSubscriptionRepository,
    ScheduledNotificationRepository,
    TimelineEventRepository,
)
from tactic.application.services.message_sender import MessageSender
from tactic.application.services.notification_sheduling_service import (
    NotificationSchedulingService,
)
from tactic.domain.entities.notification_subscription import (
    CreateNotificationSubscriptionDomain,
)
from tactic.domain.entities.sheduled_notification import (
    CreateScheduledNotificationDomain,
)
from tactic.domain.entities.timeline_event import SendEvent

# Можно использовать встроенный логгер или передавать его в класс
logger = logging.getLogger(__name__)


class NotificationSchedulingServiceImpl(NotificationSchedulingService):
    def __init__(
        self,
        scheduler: MessageSender,
        subscription_repo: NotificationSubscriptionRepository,
        event_repo: TimelineEventRepository,
        notification_repo: ScheduledNotificationRepository,
    ):
        self.scheduler = scheduler
        self.subscription_repo = subscription_repo
        self.event_repo = event_repo
        self.notification_repo = notification_repo

    def _make_job_id(
        self, chat_id: int, program_id: int, timeline_type_id: int, event_id: int
    ) -> str:
        return f"{chat_id}:{program_id}:{timeline_type_id}:{event_id}"

    def _to_noon_before(self, dt: datetime) -> datetime:
        return (dt - timedelta(days=1)).replace(hour=12, minute=0)

    async def schedule_notifications_for_program(
        self,
        user_id: int,
        chat_id: int,
        program_id: int,
        timeline_type_id: int,
    ) -> None:
        # 1. Проверка: есть ли уже подписка
        existing = await self.subscription_repo.filter(
            user_id=user_id,
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )
        if existing:
            return

        # 2. Создаём подписку
        subscription = await self.subscription_repo.add(
            CreateNotificationSubscriptionDomain(
                user_id=user_id,
                program_id=program_id,
                timeline_type_id=timeline_type_id,
            )
        )

        # 3. Получаем события, фильтруем по сроку
        timeline_events = await self.event_repo.filter(
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )
        now = datetime.now()
        timeline_events = [e for e in timeline_events if e.deadline > now]

        # 4. Создаём уведомления
        notifications = [
            CreateScheduledNotificationDomain(
                subscription_id=subscription.id,
                event_id=event.id,
                send_at=self._to_noon_before(event.deadline),
            )
            for event in timeline_events
        ]
        await self.notification_repo.add_all(notifications)

        try:
            async with asyncio.TaskGroup() as tg:
                for event in timeline_events:
                    job_id = self._make_job_id(chat_id, program_id, timeline_type_id, event.id)
                    send_event = SendEvent(
                        id=event.id,
                        message=event.event_name,
                        when=self._to_noon_before(event.deadline),
                    )
                    tg.create_task(
                        self.scheduler.schedule_message(
                            chat_id=chat_id, event=send_event, job_id=job_id
                        )
                    )
        except* Exception as e_group:
            logger.error("Ошибка при планировании уведомлений:")
            for exc in e_group.exceptions:
                logger.error("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            raise  # если нужно пробросить дальше

    async def cancel_notifications_for_program(
        self,
        subscription_id: int,
        chat_id: int,
    ) -> None:
        subscription = await self.subscription_repo.get(subscription_id)
        if subscription is None:
            return

        notifications = await self.notification_repo.filter(
            notification_subscription_id=subscription_id
        )

        # Запускаем отмену всех задач параллельно
        cancel_tasks = [
            self.scheduler.cancel_scheduled_message(
                job_id=self._make_job_id(
                    chat_id=chat_id,
                    program_id=subscription.program_id,
                    timeline_type_id=subscription.timeline_type_id,
                    event_id=notif.event_id,
                )
            )
            for notif in notifications
        ]
        await asyncio.gather(*cancel_tasks)

        # Удаляем из БД
        await self.notification_repo.delete_all([n.id for n in notifications])
        await self.subscription_repo.delete(subscription_id)
