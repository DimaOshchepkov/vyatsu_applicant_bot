

from tactic.application.services.message_sender import MessageSender
from tactic.domain.entities.timeline_event import SendEvent


class NotificationSchedulingService:
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

    def _make_job_id(self, chat_id: int, program_id: int, timeline_type_id: int, event_id: int) -> str:
        return f"{chat_id}:{program_id}:{timeline_type_id}:{event_id}"
    

    async def schedule_notifications_for_program(
        self,
        user_id: int,
        chat_id: int,
        program_id: int,
        timeline_type_id: int,
    ) -> None:
        subscription = await self.subscription_repo.get_or_create(
            user_id=user_id,
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )

        events = await self.event_repo.get_events_by_program_and_type(
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )

        event_dtos = [
            SendEvent(id=e.id, when=e.deadline, message=e.event_name.name)
            for e in events
        ]

        await self.notification_repo.bulk_create(subscription.id, event_dtos)

        for event in event_dtos:
            job_id = self._make_job_id(chat_id, program_id, timeline_type_id, event.id)
            await self.scheduler.schedule_message(chat_id=chat_id, event=event, job_id=job_id)

    async def cancel_notifications_for_program(
        self,
        user_id: int,
        chat_id: int,
        program_id: int,
        timeline_type_id: int,
    ) -> None:
        subscription = await self.subscription_repo.get_by_fields(
            user_id=user_id,
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )
        if not subscription:
            return

        notifications = await self.notification_repo.get_by_subscription_id(subscription.id)

        for n in notifications:
            job_id = self._make_job_id(chat_id, program_id, timeline_type_id, n.event_id)
            await self.scheduler.cancel_scheduled_message(job_id)

        await self.notification_repo.delete_by_subscription_id(subscription.id)
        await self.subscription_repo.delete(subscription.id)
