from typing import Protocol

from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.domain.entities.exam import Exam
from tactic.domain.entities.user import User
from tactic.domain.value_objects.user import UserId

from abc import ABC, abstractmethod
from typing import List


class UserRepository(Protocol):
    """User repository interface"""

    async def create(self, user: User) -> User:
        raise NotImplementedError

    async def exists(self, user_id: UserId) -> bool:
        raise NotImplementedError


class ExamRepository(ABC):
    
    @abstractmethod
    async def get_all(self) -> List[Exam]:
        raise NotImplementedError
    
    
class CategoryRepository(ABC):
    
    @abstractmethod
    async def get_category_tree(self) -> List[CategoryNodeModel]:
        raise NotImplementedError