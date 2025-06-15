from typing import List

from tactic.application.common.repositories import QuestionRepository
from tactic.domain.entities.question import QuestionDomain


class GetQuestionsByCategoryIdUseCase:

    def __init__(self, question_repository: QuestionRepository):
        self.question_repository = question_repository

    async def __call__(self, category_id: int) -> List[QuestionDomain]:
        return await self.question_repository.get_questions_by_category_id(category_id)
