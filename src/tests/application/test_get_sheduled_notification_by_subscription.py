from datetime import date, datetime, timedelta
from typing import Annotated, List
from unittest.mock import AsyncMock

import pytest

from shared.models import ScheduledNotification, TimelineEvent, TimelineEventName
from tactic.application.common.repositories import (
    ScheduledNotificationRepository,
    TimelineEventNameRepository,
    TimelineEventRepository,
)
from tactic.application.use_cases.get_sheduled_notification_by_subscription import (
    GetScheduledNotificationsBySubscriptionUseCase,
)
from tactic.domain.entities.sheduled_notification import ScheduledNotificationDomain
from tactic.domain.entities.timeline_event import TimelineEventDomain
from tactic.domain.entities.timeline_event_name import TimelineEventNameDomain

NotificationRepo = Annotated[ScheduledNotificationRepository, AsyncMock]
EventRepo = Annotated[TimelineEventRepository, AsyncMock]
NameRepo = Annotated[TimelineEventNameRepository, AsyncMock]


@pytest.fixture
def notification_repo() -> NotificationRepo:
    return AsyncMock(spec=ScheduledNotificationRepository)


@pytest.fixture
def event_repo() -> EventRepo:
    return AsyncMock(spec=TimelineEventRepository)


@pytest.fixture
def name_repo() -> NameRepo:
    return AsyncMock(spec=TimelineEventNameRepository)


@pytest.fixture
def usecase(
    notification_repo: NotificationRepo,
    event_repo: EventRepo,
    name_repo: NameRepo,
) -> GetScheduledNotificationsBySubscriptionUseCase:
    return GetScheduledNotificationsBySubscriptionUseCase(
        notification_repo, event_repo, name_repo
    )


@pytest.mark.asyncio
async def test_returns_empty_list_if_no_notifications(usecase, notification_repo):
    notification_repo.filter.return_value = []

    result = await usecase(subscription_id=1)

    assert result == []
    notification_repo.filter.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_returns_dto_for_single_notification(
    usecase, notification_repo, event_repo, name_repo
):
    # Setup test data
    notification = ScheduledNotificationDomain(
        id=1,
        subscription_id=1,
        event_id=10,
        send_at=datetime.today()+ timedelta(days=1),
    )
    event = TimelineEventDomain(
        id=10,
        name_id=100,
        binding_id=-1,
        deadline=date.today() + timedelta(days=2),
    )
    name = TimelineEventNameDomain(id=100, name="Подача документов")

    # Setup mocks
    notification_repo.filter.return_value = [notification]
    event_repo.get_many.return_value = [event]
    name_repo.get_many.return_value = [name]

    # Run usecase
    result = await usecase(subscription_id=1)

    # Assertions
    assert len(result) == 1
    dto = result[0]
    assert dto.id == notification.id
    assert dto.event_name == name.name
    assert dto.send_at == notification.send_at


@pytest.mark.asyncio
async def test_skips_notification_with_missing_event(
    usecase, notification_repo, event_repo, name_repo
):
    notification = ScheduledNotificationDomain(
        id=1,
        subscription_id=1,
        event_id=999,  # ID, которого не будет в events
        send_at=datetime.now(),
    )
    notification_repo.filter.return_value = [notification]
    event_repo.get_many.return_value = []  # simulate missing event
    name_repo.get_many.return_value = []

    result = await usecase(subscription_id=1)

    assert result == []


@pytest.mark.asyncio
async def test_uses_fallback_for_missing_event_name(
    usecase, notification_repo, event_repo, name_repo
):
    notification = ScheduledNotificationDomain(
        id=1,
        subscription_id=1,
        event_id=10,
        send_at=datetime.today(),
    )
    event = TimelineEventDomain(
        id=10,
        name_id=999,  # name_id не будет в name_map
        binding_id=-1,
        deadline=date.today(),
    )
    notification_repo.filter.return_value = [notification]
    event_repo.get_many.return_value = [event]
    name_repo.get_many.return_value = []

    result = await usecase(subscription_id=1)

    assert len(result) == 1
    assert result[0].event_name == "Неизвестное событие"
