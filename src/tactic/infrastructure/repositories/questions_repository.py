
from typing import List

from sqlalchemy import select
from tactic.application.common.repositories import QuestionRepository
from tactic.domain.entities.question import QuestionDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from shared.models import Question
from sqlalchemy.ext.asyncio import AsyncSession


class QuestionRepositoryImpl(BaseRepository[QuestionDomain, Question], QuestionRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, QuestionDomain, Question)
        
        
    async def get_questions_by_category_id(self, category_id: int) -> List[QuestionDomain]:
        stmt = select(Question).where(Question.category_id == category_id)
        result = await self.db.execute(stmt)
        return [self.to_domain(q) for q in result.scalars().all()]