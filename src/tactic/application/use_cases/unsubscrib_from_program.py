from tactic.application.services.notification_sheduling_service import (
    NotificationSchedulingService,
)


class UnsubscribeFromProgramUseCase:
    def __init__(
        self,
        scheduling_service: NotificationSchedulingService,
    ):
        self.scheduling_service = scheduling_service

    async def __call__(
        self,
        subscription_id: int,
        chat_id: int,
    ) -> None:
        await self.scheduling_service.cancel_notifications_for_program(
            subscription_id=subscription_id,
            chat_id=chat_id,
        )
