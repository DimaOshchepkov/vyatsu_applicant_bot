from datetime import date, datetime, timedelta
from typing import Annotated
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot  # Для примера с aiogram
from arq import ArqRedis
from arq.jobs import Job
from pytest_mock import MockerFixture

import tactic.infrastructure.telegram.telegram_message_sender as telegram_module
from tactic.domain.entities.timeline_event import SendEvent, TimelineEventDTO
from tactic.infrastructure.telegram.telegram_message_sender import (
    TelegramMessageSender,  # Для клиента arq
)


@pytest.fixture
def mock_bot(mocker: MockerFixture) -> Annotated[Bot, AsyncMock]:
    return mocker.AsyncMock(spec=Bot)  # Подразумеваем, что используем aiogram.Bot


@pytest.fixture
def mock_redis(mocker: MockerFixture) -> Annotated[ArqRedis, AsyncMock]:
    redis = mocker.AsyncMock(spec=ArqRedis)
    redis.enqueue_job = mocker.AsyncMock()
    return redis


@pytest.fixture
def sender(mock_redis):
    return TelegramMessageSender(mock_redis)


@pytest.fixture
def fake_event():
    return SendEvent(
        id=1,
        when=datetime.now() + timedelta(days=2),
        message="Test Event",
    )


@pytest.fixture
def mock_job(mocker: MockerFixture) -> Annotated[Job, AsyncMock]:
    job_mock = AsyncMock(spec=Job)
    job_mock.status = AsyncMock()
    job_mock.abort = AsyncMock()
    return job_mock


@pytest.mark.asyncio
async def test_schedule_message_future(sender, fake_event, mock_redis):
    # Сдвигаем дату далеко в будущее, чтобы delay точно был положительным
    fake_event.when = datetime.now() + timedelta(days=5)

    await sender.schedule_message(chat_id=123, event=fake_event)

    mock_redis.enqueue_job.assert_awaited_once()
    args, kwargs = mock_redis.enqueue_job.call_args
    assert kwargs["chat_id"] == 123
    assert kwargs["text"] == fake_event.message
    assert "_defer_by" in kwargs
    assert "_job_id" in kwargs
    assert kwargs["_defer_by"] > 0


# Тест планирования сообщения в прошлом
@pytest.mark.asyncio
async def test_schedule_message_past(
    sender: TelegramMessageSender, fake_event, mock_redis, mocker: MockerFixture
):
    fake_event.when = datetime.now() - timedelta(days=1)  # deadline в прошлом
    await sender.schedule_message(chat_id=123, event=fake_event)

    mock_redis.enqueue_job.assert_not_called()


@pytest.mark.asyncio
async def test_cancel_scheduled_message_found(
    sender: TelegramMessageSender,
    fake_event,
    mocker: MockerFixture,
    mock_job,
):
    mock_job.status.return_value = "queued"
    mocker.patch.object(telegram_module, "Job", return_value=mock_job)

    await sender.cancel_scheduled_message(chat_id=123, event_id=fake_event.id)

    mock_job.abort.assert_awaited_once()


# Тест отмены запланированного сообщения (не найдено в очереди)
@pytest.mark.asyncio
async def test_cancel_scheduled_message_not_found(
    sender: TelegramMessageSender,
    fake_event: TimelineEventDTO,
    mocker: MockerFixture,
    mock_job,
):
    mock_job.status.return_value = "not_found"
    mocker.patch.object(telegram_module, "Job", return_value=mock_job)

    await sender.cancel_scheduled_message(chat_id=123, event_id=fake_event.id)

    mock_job.abort.assert_not_called()



