from typing import Annotated
import pytest
from unittest.mock import AsyncMock, MagicMock

from tactic.application.common.repositories import NotificationSubscriptionRepository, ProgramRepository, TimelineTypeRepository
from tactic.application.use_cases.get_list_subsriptions import GetListSubscriptionsUseCase
from tactic.domain.entities.notification_subscription import NotificationSubscriptionDTO
from tactic.domain.entities.timeline_type import PaymentType

NotificationRepo = Annotated[NotificationSubscriptionRepository, AsyncMock]
ProgramRepo = Annotated[ProgramRepository, AsyncMock]
TimelineTypeRepo = Annotated[TimelineTypeRepository, AsyncMock]

@pytest.fixture
def subscription_repo() -> NotificationRepo:
    return AsyncMock(spec=NotificationSubscriptionRepository)

@pytest.fixture
def program_repo() -> ProgramRepo:
    return AsyncMock(spec=ProgramRepository)

@pytest.fixture
def timeline_type_repo() -> TimelineTypeRepo:
    return AsyncMock(spec=TimelineTypeRepository)


@pytest.mark.asyncio
async def test_get_list_subscriptions_use_case(
    subscription_repo,
    program_repo,
    timeline_type_repo,
):
    # --- Arrange ---
    user_id = 1

    # Моки подписки
    subscription_repo.filter.return_value = [
        MagicMock(id=1, program_id=100, timeline_type_id=PaymentType.BUDGET.value)
    ]

    # Моки программ
    program_repo.get_many.return_value = [
        MagicMock(id=100, title="Программа тест")
    ]

    # Моки типов таймлайна
    timeline_type_repo.get_many.return_value = [
        MagicMock(id=PaymentType.BUDGET.value)
    ]

    use_case = GetListSubscriptionsUseCase(
        subscription_repo, program_repo, timeline_type_repo
    )

    # --- Act ---
    result = await use_case(user_id)

    # --- Assert ---
    assert len(result) == 1
    assert isinstance(result[0], NotificationSubscriptionDTO)
    assert result[0].id == 1
    assert result[0].program_title == "Программа тест"
    assert result[0].timeline_type_name == "Бюджет" 