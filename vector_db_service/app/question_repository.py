from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from app.models import QuestionItem
from sqlalchemy import ForeignKey, Integer, String, Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )

    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )

    children: Mapped[List["Category"]] = relationship(
        "Category", back_populates="parent"
    )

    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="category"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )

    category: Mapped["Category"] = relationship("Category", back_populates="questions")


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
