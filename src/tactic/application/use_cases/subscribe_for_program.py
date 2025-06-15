from tactic.application.services.notification_sheduling_service import (
    NotificationSchedulingService,
)


class SubscribeForProgramUseCase:
    def __init__(self, sheduler: NotificationSchedulingService):
        self.sheduler = sheduler

    async def __call__(
        self, user_id: int, chat_id: int, program_id: int, timeline_type_id: int
    ) -> None:
        await self.sheduler.schedule_notifications_for_program(
            user_id=user_id,
            chat_id=chat_id,
            program_id=program_id,
            timeline_type_id=timeline_type_id,
        )
