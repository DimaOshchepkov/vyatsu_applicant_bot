from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from sqlalchemy import BigInteger
from sqlalchemy import Integer, String, ForeignKey, Text

from tactic.domain.value_objects.user import UserId


from typing import List, Optional
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UserId] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)

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
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="questions")
