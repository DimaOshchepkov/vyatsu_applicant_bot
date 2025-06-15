import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from arq import ArqRedis
from arq.jobs import Job

from tactic.application.services.message_sender import MessageSender
from tactic.domain.entities.timeline_event import SendEvent


class TelegramMessageSender(MessageSender):
    """
    Отправляет запланированные сообщения через Telegram, используя arq для очередей.
    """

    def __init__(
        self,
        redis: ArqRedis,
        tz: ZoneInfo = ZoneInfo("Europe/Moscow"),
    ):
        """
        Инициализирует отправитель сообщений.

        :param bot: Экземпляр бота для отправки сообщений.
        :param redis: Экземпляр клиента arq.
        :param tz: Часовой пояс для всех операций со временем.
        """
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
    
    async def _abort_now(self, job: Job) -> bool:
        try:
            return await job.abort(timeout=0)
        except TimeoutError:
            return True

    async def schedule_message(
        self, chat_id: int, event: SendEvent, job_id: str | None = None
    ):
        """
        Планирует отправку одного сообщения.

        :param chat_id: ID чата для отправки.
        :param event: DTO события.
        """
        when = event.when
        now = datetime.now()
        delay = (when - now).total_seconds()
        if job_id is None:
            job_id = self._make_job_id(chat_id, event.id)
        text = event.message

        # Если время уже прошло, отправляем немедленно
        if delay <= 0:
            self.logger.warning(
                f"Time for event {event.id} has already passed. Sending now."
            )
            self.logger.warning("Положено просрочненное сообщение")
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

    async def cancel_scheduled_message(
        self, chat_id: int | None = None, event_id: int | None = None, job_id: str | None = None
    ):
        """
        Отменяет запланированную отправку одного сообщения.

        :param chat_id: ID чата (для будущего использования, если потребуется).
        :param event: DTO события.
        """
        if job_id is None:
            if chat_id is None or event_id is None:
                raise ValueError(
                    "Необходимо передать либо job_id, либо chat_id и event."
                )
            job_id = self._make_job_id(chat_id, event_id)
        job = Job(job_id, self.redis)

        try:
            status = await job.status()
            if status != "not_found":
                await self._abort_now(job)
                self.logger.info(f"Aborted scheduled message (Job ID: {job_id})")
            else:
                self.logger.warning(f"Scheduled message not found. Nothing to cancel.")
        except Exception as e:
            # arq может выбросить исключение, если job не найден, в зависимости от версии
            self.logger.error(
                f"Could not find or abort job (Job ID: {job_id}). Reason: {e}",
                exc_info=True,
            )
