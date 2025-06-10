import logging
from datetime import date, datetime, time, timedelta
from typing import List
from zoneinfo import ZoneInfo

from aiogram import Bot
from arq import ArqRedis
from arq.jobs import Job

from tactic.application.services.message_sender import MessageSender
from tactic.domain.entities.timeline_event import TimelineEventDTO


class TelegramMessageSender(MessageSender):
    """
    Отправляет запланированные сообщения через Telegram, используя arq для очередей.
    """

    def __init__(
        self,
        bot: Bot,
        redis: ArqRedis,
        tz: ZoneInfo = ZoneInfo("Europe/Moscow"),
    ):
        """
        Инициализирует отправитель сообщений.

        :param bot: Экземпляр бота для отправки сообщений.
        :param redis: Экземпляр клиента arq.
        :param tz: Часовой пояс для всех операций со временем.
        """
        self.bot = bot
        self.redis = redis
        self.tz = tz
        self.logger = logging.getLogger(self.__class__.__name__)

    def _make_job_id(self, chat_id: int, timeline_event_id: int) -> str:
        """
        Создает детерминированный и уникальный ID для задачи
        на основе ID чата и ID события.

        :param chat_id: ID чата.
        :param timeline_event_id: ID события.
        """

        return f"send_event:{chat_id}:{timeline_event_id}"


    async def schedule_message(self, chat_id: int, event: TimelineEventDTO):
        """
        Планирует отправку одного сообщения.

        :param chat_id: ID чата для отправки.
        :param event: DTO события.
        """
        when = event.deadline
        now = datetime.now()
        delay = (when - now).total_seconds()
        job_id = self._make_job_id(chat_id, event.id)
        text = event.event_name

        # Если время уже прошло, отправляем немедленно
        if delay <= 0:
            self.logger.warning(
                f"Time for event {event.id} has already passed. Sending now."
            )
            self.logger.warning("Отправлено просроченное сообщение")
            await self.bot.send_message(chat_id, text)
            return

        # Иначе ставим в очередь
        await self.redis.enqueue_job(
            "send_delayed_message",  # Имя воркера, который будет обрабатывать задачу
            chat_id=chat_id,
            text=text,
            _defer_by=delay,
            _job_id=job_id,
        )
        self.logger.info(
            f"Scheduled message for event {event.id} to be sent at {when.isoformat()}"
        )

    async def cancel_scheduled_message(self, chat_id: int, event: TimelineEventDTO):
        """
        Отменяет запланированную отправку одного сообщения.

        :param chat_id: ID чата (для будущего использования, если потребуется).
        :param event: DTO события.
        """
        job_id = self._make_job_id(chat_id, event.id)
        job = Job(job_id, self.redis)

        try:
            status = await job.status()
            if status != "not_found":
                await job.abort()
                self.logger.info(
                    f"Aborted scheduled message for event {event.id} (Job ID: {job_id})"
                )
            else:
                self.logger.warning(
                    f"Scheduled message for event {event.id} not found. Nothing to cancel."
                )
        except Exception as e:
            # arq может выбросить исключение, если job не найден, в зависимости от версии
            self.logger.error(
                f"Could not find or abort job for event {event.id}. Reason: {e}",
                exc_info=True,
            )

    async def schedule_messages_bulk(
        self, chat_id: int, events: List[TimelineEventDTO]
    ):
        """
        Планирует отправку нескольких сообщений.

        :param chat_id: ID чата для отправки.
        :param events: Список DTO событий.
        """
        self.logger.info(
            f"Starting bulk scheduling for {len(events)} events for chat {chat_id}."
        )
        for event in events:
            await self.schedule_message(chat_id, event)
        self.logger.info(f"Finished bulk scheduling for chat {chat_id}.")

    async def cancel_scheduled_messages_bulk(
        self, chat_id: int, events: List[TimelineEventDTO]
    ):
        """
        Отменяет отправку нескольких запланированных сообщений.

        :param chat_id: ID чата.
        :param events: Список DTO событий для отмены.
        """
        self.logger.info(
            f"Starting bulk cancellation for {len(events)} events for chat {chat_id}."
        )
        for event in events:
            await self.cancel_scheduled_message(chat_id, event)
        self.logger.info(f"Finished bulk cancellation for chat {chat_id}.")
