from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from tactic.application.create_user import CreateUser

from tactic.application.recognize_exam import RecognizeExamUseCase
from tactic.domain.services.user import UserService

from tactic.infrastructure.db.repositories.user import UserRepositoryImpl
from tactic.infrastructure.db.uow import SQLAlchemyUoW

from tactic.infrastructure.recognize_exam_fuzzy_wuzzy import RecognizeExamFuzzywuzzy
from tactic.infrastructure.repositories.json_exam_repository import JsonExamRepository
from tactic.presentation.interactor_factory import InteractorFactory

from tactic.settings import settings

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
        repo = JsonExamRepository(file_path=settings.exam_json_path)
        service = await RecognizeExamFuzzywuzzy.create(exam_repository=repo, threshold=settings.threshold)
        yield RecognizeExamUseCase(service)
