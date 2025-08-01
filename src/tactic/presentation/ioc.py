from contextlib import asynccontextmanager
from typing import AsyncIterator

from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tactic.application.common.fabrics import RecognizeExamFactory
from tactic.application.services.recognize_program import RecognizeProgram
from tactic.application.use_cases.create_user import CreateUser
from tactic.application.use_cases.get_all_contest_types import GetAllContestTypesUseCase
from tactic.application.use_cases.get_all_education_levels import (
    GetAllEducationLevelsUseCase,
)
from tactic.application.use_cases.get_all_study_forms import GetAllStudyFormsUseCase
from tactic.application.use_cases.get_categories import GetCategoriesUseCase

from tactic.application.use_cases.get_filtered_contest_type import (
    GetFilterdContestTypesUseCase,
)
from tactic.application.use_cases.get_filtered_programs import GetFilterdProgramsUseCase
from tactic.application.use_cases.get_filtered_study_forms import (
    GetFilterdStudyFormsUseCase,
)
from tactic.application.use_cases.get_list_subsriptions import (
    GetListSubscriptionsUseCase,
)
from tactic.application.use_cases.get_questions import GetQuestionsUseCase
from tactic.application.use_cases.get_questions_by_category_id import (
    GetQuestionsByCategoryIdUseCase,
)
from tactic.application.use_cases.get_sheduled_notification_by_subscription import (
    GetScheduledNotificationsBySubscriptionUseCase,
)
from tactic.application.use_cases.get_timeline_event import GetTimelineEventUseCase
from tactic.application.use_cases.recognize_exam import RecognizeExamUseCase
from tactic.application.use_cases.recognize_program import RecognizeProgramUseCase
from tactic.application.use_cases.send_notification import SendNotificationUseCase
from tactic.application.use_cases.subscribe_for_program import (
    SubscribeForProgramUseCase,
)
from tactic.application.use_cases.unsubscrib_from_program import (
    UnsubscribeFromProgramUseCase,
)
from tactic.domain.services.user import UserService
from tactic.infrastructure.db.uow import SQLAlchemyUoW
from tactic.infrastructure.notificaton_message_sheduling_service import (
    NotificationSchedulingServiceImpl,
)
from tactic.infrastructure.recognize_exam_rapid_wuzzy_factory import (
    RecognizeExamRapidWuzzyFactory,
)
from tactic.infrastructure.repositories.category_repository import (
    CategoryRepositoryImpl,
)
from tactic.infrastructure.repositories.contest_type_repository import (
    ContestTypeRepositoryImpl,
)
from tactic.infrastructure.repositories.db_subject_repository import DbSubjectRepository
from tactic.infrastructure.repositories.education_level_repository import (
    EducationLevelRepositoryImpl,
)
from tactic.infrastructure.repositories.notification_subscription_repository import (
    NotificationSubscriptionRepositoryImpl,
)
from tactic.infrastructure.repositories.program_repository import ProgramRepositoryImpl
from tactic.infrastructure.repositories.questions_repository import (
    QuestionRepositoryImpl,
)
from tactic.infrastructure.repositories.sheduled_notification_repository import (
    ScheduledNotificationRepositoryImpl,
)
from tactic.infrastructure.repositories.study_form_repository import (
    StudyFormRepositoryImpl,
)
from tactic.infrastructure.repositories.timeline_event_name_repository import (
    TimelineEventNameRepositoryImpl,
)
from tactic.infrastructure.repositories.timeline_event_repository import (
    TimelineEventRepositoryImpl,
)
from tactic.infrastructure.repositories.timeline_type_repository import (
    TimelineTypeRepositoryImpl,
)
from tactic.infrastructure.repositories.user import UserRepositoryImpl
from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot
from tactic.infrastructure.telegram.telegram_message_sender import TelegramMessageSender
from tactic.presentation.interactor_factory import InteractorFactory


class IoC(InteractorFactory):
    _session_factory: async_sessionmaker[AsyncSession]
    _bot: RateLimitedBot
    _arq_redis: ArqRedis
    _recognize_program: RecognizeProgram
    _exam_recognize_factory: RecognizeExamFactory = RecognizeExamRapidWuzzyFactory()

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        bot: RateLimitedBot,
        arq_redis: ArqRedis,
        recognize_program: RecognizeProgram,
    ):
        self._session_factory = session_factory
        self._bot = bot
        self._arq_redis = arq_redis
        self._recognize_program = recognize_program

    @asynccontextmanager
    async def create_user(self) -> AsyncIterator[CreateUser]:
        async with self._session_factory() as session:
            async with session.begin():
                uow = SQLAlchemyUoW(session)
                repo = UserRepositoryImpl(session)

                yield CreateUser(
                    repository=repo,
                    uow=uow,
                    user_service=UserService(),
                )

    @asynccontextmanager
    async def recognize_exam(self) -> AsyncIterator[RecognizeExamUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = DbSubjectRepository(session)
                yield RecognizeExamUseCase(repo, self._exam_recognize_factory)

    @asynccontextmanager
    async def get_categories(self) -> AsyncIterator[GetCategoriesUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = CategoryRepositoryImpl(session)

                yield GetCategoriesUseCase(repo)

    @asynccontextmanager
    async def get_questions(self) -> AsyncIterator[GetQuestionsUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = QuestionRepositoryImpl(session)

                yield GetQuestionsUseCase(repo)

    @asynccontextmanager
    async def get_questions_by_category_id(
        self,
    ) -> AsyncIterator[GetQuestionsByCategoryIdUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = QuestionRepositoryImpl(session)

                yield GetQuestionsByCategoryIdUseCase(repo)


    @asynccontextmanager
    async def get_all_education_levels(
        self,
    ) -> AsyncIterator[GetAllEducationLevelsUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                education_levels_repo = EducationLevelRepositoryImpl(session)

                yield GetAllEducationLevelsUseCase(education_levels_repo)

    @asynccontextmanager
    async def get_all_contest_types(self) -> AsyncIterator[GetAllContestTypesUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = ContestTypeRepositoryImpl(session)

                yield GetAllContestTypesUseCase(repo)

    @asynccontextmanager
    async def get_all_study_forms(self) -> AsyncIterator[GetAllStudyFormsUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = StudyFormRepositoryImpl(session)

                yield GetAllStudyFormsUseCase(repo)

    @asynccontextmanager
    async def get_filtered_programs(self) -> AsyncIterator[GetFilterdProgramsUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = ProgramRepositoryImpl(session)

                yield GetFilterdProgramsUseCase(repo)

    @asynccontextmanager
    async def send_telegram_notification(
        self,
    ) -> AsyncIterator[SendNotificationUseCase]:
        """
        IoC-контейнер, который создает и предоставляет UseCase с настроенными зависимостями.
        """

        sender = TelegramMessageSender(self._arq_redis)
        yield SendNotificationUseCase(sender)

    @asynccontextmanager
    async def get_timeline_events(self) -> AsyncIterator[GetTimelineEventUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = TimelineEventRepositoryImpl(session)

                yield GetTimelineEventUseCase(repo)

    @asynccontextmanager
    async def recognize_program(self) -> AsyncIterator[RecognizeProgramUseCase]:
        yield RecognizeProgramUseCase(self._recognize_program)

    def __create_notification_scheduling_service(
        self,
        session: AsyncSession,
    ) -> NotificationSchedulingServiceImpl:

        subscription_repo = NotificationSubscriptionRepositoryImpl(session)
        notification_repo = ScheduledNotificationRepositoryImpl(session)
        event_repo = TimelineEventRepositoryImpl(session)
        scheduler = TelegramMessageSender(self._arq_redis)

        return NotificationSchedulingServiceImpl(
            scheduler=scheduler,
            subscription_repo=subscription_repo,
            event_repo=event_repo,
            notification_repo=notification_repo,
        )

    @asynccontextmanager
    async def subscribe_for_program(self) -> AsyncIterator[SubscribeForProgramUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                sheduler = self.__create_notification_scheduling_service(session)

                yield SubscribeForProgramUseCase(sheduler=sheduler)

    @asynccontextmanager
    async def get_list_subscriptions(
        self,
    ) -> AsyncIterator[GetListSubscriptionsUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                subscription_repo = NotificationSubscriptionRepositoryImpl(session)
                program_repo = ProgramRepositoryImpl(session)
                timeline_type_repo = TimelineTypeRepositoryImpl(session)

                yield GetListSubscriptionsUseCase(
                    subscription_repo=subscription_repo,
                    program_repo=program_repo,
                    timeline_type_repo=timeline_type_repo,
                )

    @asynccontextmanager
    async def unsubscribe_from_program(
        self,
    ) -> AsyncIterator[UnsubscribeFromProgramUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                scheduling_service = self.__create_notification_scheduling_service(
                    session
                )

                yield UnsubscribeFromProgramUseCase(
                    scheduling_service=scheduling_service
                )

    @asynccontextmanager
    async def get_sheduled_notification(
        self,
    ) -> AsyncIterator[GetScheduledNotificationsBySubscriptionUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                notification_repo = ScheduledNotificationRepositoryImpl(session)
                event_repo = TimelineEventRepositoryImpl(session)
                name_repo = TimelineEventNameRepositoryImpl(session)

                yield GetScheduledNotificationsBySubscriptionUseCase(
                    notification_repo=notification_repo,
                    event_repo=event_repo,
                    name_repo=name_repo,
                )

    @asynccontextmanager
    async def get_filtered_study_forms(
        self,
    ) -> AsyncIterator[GetFilterdStudyFormsUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = StudyFormRepositoryImpl(session)

                yield GetFilterdStudyFormsUseCase(repo)

    @asynccontextmanager
    async def get_filtered_contest_types(
        self,
    ) -> AsyncIterator[GetFilterdContestTypesUseCase]:
        async with self._session_factory() as session:
            async with session.begin():
                repo = ContestTypeRepositoryImpl(session)

                yield GetFilterdContestTypesUseCase(repo)
