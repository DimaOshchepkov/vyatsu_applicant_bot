from abc import ABC, abstractmethod


class NotificationSchedulingService(ABC):

    @abstractmethod
    async def schedule_notifications_for_program(
        self,
        user_id: int,
        chat_id: int,
        program_id: int,
        timeline_type_id: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def cancel_notifications_for_program(
        self,
        subscription_id: int,
        chat_id: int,
    ) -> None:
        raise NotImplementedError
