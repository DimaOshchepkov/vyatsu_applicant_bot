from typing import Generic, List, Optional, TypeVar

from tactic.domain.entities.category import CategoryDomain
from tactic.domain.entities.question import QuestionDomain

T = TypeVar("T")

class BaseCache(Generic[T]):
    _value: Optional[T] = None

    @classmethod
    def set(cls, value: T) -> None:
        cls._value = value

    @classmethod
    def get(cls) -> Optional[T]:
        return cls._value

    @classmethod
    def clear(cls) -> None:
        cls._value = None
        
        
class CategoryCache(BaseCache[List[CategoryDomain]]):
    pass


class QuestionCache(BaseCache[List[QuestionDomain]]):
    pass