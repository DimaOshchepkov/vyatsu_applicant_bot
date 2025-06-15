import logging
from typing import List

from tactic.application.common.repositories import (
    NotificationSubscriptionRepository,
    ProgramRepository,
    TimelineTypeRepository,
)
from tactic.domain.entities.notification_subscription import NotificationSubscriptionDTO
from tactic.domain.entities.timeline_type import PaymentType

logger = logging.getLogger(__name__)


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
        self.type_map = {
                PaymentType.BUDGET.value: "Бюджет",
                PaymentType.PAID.value: "Платно",
            }

    async def __call__(self, user_id: int) -> List[NotificationSubscriptionDTO]:
        logger.info("Запущен GetListSubscriptionsUseCase для user_id=%s", user_id)

        subscriptions_domain = await self.subscription_repo.filter(user_id=user_id)
        logger.debug("Найдено %d подписок", len(subscriptions_domain))

        if not subscriptions_domain:
            logger.warning("Подписок не найдено для user_id=%s", user_id)
            return []

        program_ids = {sub.program_id for sub in subscriptions_domain}
        timeline_type_ids = {sub.timeline_type_id for sub in subscriptions_domain}
        logger.debug("Собраны program_ids: %s", program_ids)
        logger.debug("Собраны timeline_type_ids: %s", timeline_type_ids)

        programs = await self.program_repo.get_many(program_ids)
        timeline_types = await self.timeline_type_repo.get_many(timeline_type_ids)
        logger.debug(
            "Найдено программ: %d, типов таймлайнов: %d",
            len(programs),
            len(timeline_types),
        )

        program_map = {p.id: p for p in programs}
        timeline_type_map = {t.id: t for t in timeline_types}

        subscriptions_dto = []
        for sub in subscriptions_domain:
            program = program_map.get(sub.program_id)
            timeline_type = timeline_type_map.get(sub.timeline_type_id) 

            timeline_type_name = self.type_map.get(sub.timeline_type_id, "Неизвестно")
            if not program:
                logger.warning("Программа с id=%s не найдена", sub.program_id)
            if not timeline_type:
                logger.warning("Тип таймлайна с id=%s не найден", sub.timeline_type_id)

            if program and timeline_type:
                subscriptions_dto.append(
                    NotificationSubscriptionDTO(
                        id=sub.id,
                        program_title=program.title,
                        timeline_type_name=timeline_type_name,
                    )
                )

        logger.info("Формирование DTO завершено: %d элементов", len(subscriptions_dto))
        return subscriptions_dto
