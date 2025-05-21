from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tactic.application.create_user import CreateUser
from tactic.application.get_categories import GetCategoriesUseCase
from tactic.application.get_eligible_program_ids_use_case import (
    GetEligibleProgramIdsUseCase,
)
from tactic.application.get_questions import GetQuestionsUseCase
from tactic.application.get_questions_by_category_id import (
    GetQuestionsByCategoryIdUseCase,
)
from tactic.application.get_questions_category_tree import (
    GetQuestionsCategoryTreeUseCase,
)
from tactic.application.recognize_exam import RecognizeExamUseCase
from tactic.domain.services.user import UserService
from tactic.infrastructure.repositories.user import UserRepositoryImpl
from tactic.infrastructure.db.uow import SQLAlchemyUoW
from tactic.infrastructure.recognize_exam_fuzzy_wuzzy import RecognizeExamFuzzywuzzy
from tactic.infrastructure.repositories.category_repository import (
    CategoryRepositoryImpl,
)
from tactic.infrastructure.repositories.db_exam_repository import DbExamRepository
from tactic.infrastructure.repositories.json_exam_repository import (
    JsonExamRepositoryImpl,
)
from tactic.infrastructure.repositories.program_repository import ProgramRepositoryImpl
from tactic.infrastructure.repositories.questions_repository import (
    QuestionRepositoryImpl,
)
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.settings import exam_service_settings


class IoC(InteractorFactory):
    _session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

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
            repo = JsonExamRepositoryImpl(file_path=exam_service_settings.exam_json_path)
            service = await RecognizeExamFuzzywuzzy.create(
                exam_repository=repo, threshold=exam_service_settings.threshold
            )
            yield RecognizeExamUseCase(service)

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
            exam_repo = DbExamRepository(session)
            
            yield GetEligibleProgramIdsUseCase(exam_repo)
