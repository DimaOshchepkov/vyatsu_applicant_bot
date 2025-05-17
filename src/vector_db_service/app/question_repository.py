from typing import Dict, List, Optional, Tuple

from vector_db_service.app.models import QuestionItem
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Category, Question


class QuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_questions_with_path(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[List[QuestionItem], int]:
        # Загружаем все категории в кэш
        categories_stmt = select(Category)
        categories_result = await self.session.execute(categories_stmt)
        category_map: Dict[int, Category] = {
            category.id: category for category in categories_result.scalars().all()
        }

        # Получаем общее количество вопросов
        count_stmt = select(func.count()).select_from(Question)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Получаем ограниченное число вопросов с загрузкой category
        questions_stmt = select(Question).offset(offset).limit(limit)

        questions_result = await self.session.execute(questions_stmt)
        questions = questions_result.scalars().all()

        # Формируем результат
        items: List[QuestionItem] = []
        for question in questions:
            category = category_map.get(question.category_id)
            path = self._build_category_path(category, category_map)
            items.append(
                QuestionItem(
                    question=question.question, answer=question.answer or "", path=path
                )
            )

        return items, total

    def _build_category_path(
        self, category: Optional[Category], category_map: Dict[int, Category]
    ) -> List[str]:
        path: List[str] = []
        current = category
        while current:
            path.insert(0, current.title)
            current = category_map.get(current.parent_id) if current.parent_id else None
        return path
