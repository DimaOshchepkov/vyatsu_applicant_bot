
from tactic.application.common.repositories import QuestionRepository
from tactic.domain.entities.question import QuestionDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.db.models import Question
from sqlalchemy.ext.asyncio import AsyncSession


class QuestionRepositoryImpl(BaseRepository[QuestionDomain, Question], QuestionRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, QuestionDomain, Question)