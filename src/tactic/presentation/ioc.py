from contextlib import asynccontextmanager
from typing import AsyncIterator

from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tactic.application.common.fabrics import (
    RecognizeExamFactory,
    RecognizeProgramFactory,
)
from tactic.application.common.repositories import ProgramRepository
from tactic.application.services.recognize_program import RecognizeProgram
from tactic.application.use_cases.create_user import CreateUser
from tactic.application.use_cases.get_all_contest_types import GetAllContestTypesUseCase
from tactic.application.use_cases.get_all_education_levels import (
    GetAllEducationLevelsUseCase,
)
from tactic.application.use_cases.get_all_study_forms import GetAllStudyFormsUseCase
from tactic.application.use_cases.get_categories import GetCategoriesUseCase
from tactic.application.use_cases.get_eligible_program_ids_use_case import (
    GetEligibleProgramIdsUseCase,
)
from tactic.application.use_cases.get_filtered_programs import GetFilterdProgramsUseCase
from tactic.application.use_cases.get_questions import GetQuestionsUseCase
from tactic.application.use_cases.get_questions_by_category_id import (
    GetQuestionsByCategoryIdUseCase,
)
from tactic.application.use_cases.get_questions_category_tree import (
    GetQuestionsCategoryTreeUseCase,
)
from tactic.application.use_cases.get_timeline_event import GetTimelineEventUseCase
from tactic.application.use_cases.recognize_exam import RecognizeExamUseCase
from tactic.application.use_cases.recognize_program import RecognizeProgramUseCase
from tactic.application.use_cases.send_notification import SendNotificationUseCase
from tactic.domain.services.user import UserService
from tactic.infrastructure.db.uow import SQLAlchemyUoW
from tactic.infrastructure.recognize_exam_rapid_wuzzy_factory import (
    RecognizeExamRapidWuzzyFactory,
)

from tactic.infrastructure.recognize_program_rapid_wuzzy import RecognizeProgramRapidWuzzy
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
from tactic.infrastructure.repositories.program_repository import ProgramRepositoryImpl
from tactic.infrastructure.repositories.questions_repository import (
    QuestionRepositoryImpl,
)
from tactic.infrastructure.repositories.study_form_repository import (
    StudyFormRepositoryImpl,
)
from tactic.infrastructure.repositories.timeline_event_repository import (
    TimelineEventRepositoryImpl,
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
            repo = DbSubjectRepository(session)
            yield RecognizeExamUseCase(repo, self._exam_recognize_factory)

    @asynccontextmanager
    async def get_questions_category(
        self,
    ) -> AsyncIterator[GetQuestionsCategoryTreeUseCase]:
        async with self._session_factory() as session:
            repo = CategoryRepositoryImpl(session)

            yield GetQuestionsCategoryTreeUseCase(repo)

    @asynccontextmanager
    async def get_categories(self) -> AsyncIterator[GetCategoriesUseCase]:
        async with self._session_factory() as session:
            repo = CategoryRepositoryImpl(session)

            yield GetCategoriesUseCase(repo)

    @asynccontextmanager
    async def get_questions(self) -> AsyncIterator[GetQuestionsUseCase]:
        async with self._session_factory() as session:
            repo = QuestionRepositoryImpl(session)

            yield GetQuestionsUseCase(repo)

    @asynccontextmanager
    async def get_questions_by_category_id(
        self,
    ) -> AsyncIterator[GetQuestionsByCategoryIdUseCase]:
        async with self._session_factory() as session:
            repo = QuestionRepositoryImpl(session)

            yield GetQuestionsByCategoryIdUseCase(repo)

    @asynccontextmanager
    async def get_eligible_program_ids(
        self,
    ) -> AsyncIterator[GetEligibleProgramIdsUseCase]:
        async with self._session_factory() as session:
            exam_repo = DbSubjectRepository(session)

            yield GetEligibleProgramIdsUseCase(exam_repo)

    @asynccontextmanager
    async def get_all_education_levels(
        self,
    ) -> AsyncIterator[GetAllEducationLevelsUseCase]:
        async with self._session_factory() as session:
            education_levels_repo = EducationLevelRepositoryImpl(session)

            yield GetAllEducationLevelsUseCase(education_levels_repo)

    @asynccontextmanager
    async def get_all_contest_types(self) -> AsyncIterator[GetAllContestTypesUseCase]:
        async with self._session_factory() as session:
            repo = ContestTypeRepositoryImpl(session)

            yield GetAllContestTypesUseCase(repo)

    @asynccontextmanager
    async def get_all_study_forms(self) -> AsyncIterator[GetAllStudyFormsUseCase]:
        async with self._session_factory() as session:
            repo = StudyFormRepositoryImpl(session)

            yield GetAllStudyFormsUseCase(repo)

    @asynccontextmanager
    async def get_filtered_programs(self) -> AsyncIterator[GetFilterdProgramsUseCase]:
        async with self._session_factory() as session:
            repo = ProgramRepositoryImpl(session)

            yield GetFilterdProgramsUseCase(repo)

    @asynccontextmanager
    async def send_telegram_notification(
        self,
    ) -> AsyncIterator[SendNotificationUseCase]:
        """
        IoC-контейнер, который создает и предоставляет UseCase с настроенными зависимостями.
        """

        sender = TelegramMessageSender(self._bot, self._arq_redis)
        yield SendNotificationUseCase(sender)

    @asynccontextmanager
    async def get_timeline_events(self) -> AsyncIterator[GetTimelineEventUseCase]:
        async with self._session_factory() as session:
            repo = TimelineEventRepositoryImpl(session)

            yield GetTimelineEventUseCase(repo)
            
            
    @asynccontextmanager
    async def recognize_program(self) -> AsyncIterator[RecognizeProgramUseCase]:
        yield RecognizeProgramUseCase(self._recognize_program)
