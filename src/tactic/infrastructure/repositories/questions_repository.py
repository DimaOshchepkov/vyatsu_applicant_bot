from typing import List

from aiocache import cached
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Question
from tactic.application.common.repositories import QuestionRepository
from tactic.domain.entities.question import CreateQuestionDomain, QuestionDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class QuestionRepositoryImpl(
    BaseRepository[QuestionDomain, Question, CreateQuestionDomain], QuestionRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, QuestionDomain, Question, CreateQuestionDomain)

    @cached(ttl=60, key_builder=classaware_key_builder)
    async def get_questions_by_category_id(  # type: ignore
        self, category_id: int
    ) -> List[QuestionDomain]:
        stmt = select(Question).where(Question.category_id == category_id)
        result = await self.db.execute(stmt)
        return [self.to_dto(q) for q in result.scalars().all()]
