from datetime import datetime, timedelta

from tactic.application.common.repositories import (
    NotificationSubscriptionRepository,
    ScheduledNotificationRepository,
    TimelineEventRepository,
)
from tactic.application.services.message_sender import MessageSender
from tactic.application.services.notification_sheduling_service import NotificationSchedulingService
from tactic.domain.entities.notification_subscription import (
    CreateNotificationSubscriptionDomain,
)
from tactic.domain.entities.sheduled_notification import (
    CreateScheduledNotificationDomain,
)
from tactic.domain.entities.timeline_event import SendEvent


class NotificationSchedulingServiceImpl(NotificationSchedulingService):
    def __init__(
        self,
        sender: MessageSender,
        subscription_repo: NotificationSubscriptionRepository,
        event_repo: TimelineEventRepository,
        notification_repo: ScheduledNotificationRepository,
    ):
        self.scheduler = sender
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
        subscriptions = await self.subscription_repo.filter(
            user_id=user_id,
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )
        if len(subscriptions) == 0:
            subcription = await self.subscription_repo.add(
                CreateNotificationSubscriptionDomain(
                    user_id=user_id,
                    program_id=program_id,
                    timeline_type_id=timeline_type_id,
                )
            )
        else:
            return

        timeline_events = await self.event_repo.filter(
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )
        timeline_events = [t_e for t_e in timeline_events if t_e.deadline > datetime.now()]

        sheduled_notification = [
            CreateScheduledNotificationDomain(
                subscription_id=subcription.id,
                event_id=t_e.id,
                send_at=self._to_noon_before(t_e.deadline),
            )
            for t_e in timeline_events
        ]
        await self.notification_repo.add_all(sheduled_notification)

        send_events = [
            SendEvent(
                id=e.id,
                message=e.event_name,
                when=self._to_noon_before(e.deadline),
            )
            for e in timeline_events
        ]
        for event in send_events:
            job_id = self._make_job_id(chat_id, program_id, timeline_type_id, event.id)
            await self.scheduler.schedule_message(
                chat_id=chat_id, event=event, job_id=job_id
            )

    async def cancel_notifications_for_program(
        self,
        subscription_id: int,
        chat_id: int,
    ) -> None:
        # 1. Получить все уведомления, связанные с подпиской
        subscription = await self.subscription_repo.get(subscription_id)
        if subscription is None:
            return
        notifications = await self.notification_repo.filter(
            notification_subscription_id=subscription_id
        )

        # 2. Отменить каждый в планировщике
        for notif in notifications:
            job_id = self._make_job_id(
                chat_id=chat_id,
                program_id=subscription.program_id,
                timeline_type_id=subscription.timeline_type_id,
                event_id=notif.event_id,
            )
            await self.scheduler.cancel_scheduled_message(job_id=job_id)

        await self.notification_repo.delete_all([n.id for n in notifications])
        await self.subscription_repo.delete(subscription_id)
