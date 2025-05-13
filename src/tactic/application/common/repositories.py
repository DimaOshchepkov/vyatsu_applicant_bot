from typing import Protocol

from tactic.domain.entities.category import CategoryDomain
from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.domain.entities.exam import Exam
from tactic.domain.entities.user import User
from tactic.domain.value_objects.user import UserId
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")  # доменная модель

class IBaseRepository(ABC, Generic[T]):
    
    @abstractmethod
    async def get(self, id: int) -> Optional[T]: ...
    
    @abstractmethod
    async def get_all(self) -> List[T]: ...
    
    @abstractmethod
    async def add(self, entity: T) -> T: ...
    
    @abstractmethod
    async def update(self, entity: T) -> T: ...
    
    @abstractmethod
    async def delete(self, entity: T) -> None: ...



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
    
    
class CategoryRepository(IBaseRepository[CategoryDomain], ABC):
    
    @abstractmethod
    async def get_category_tree(self) -> List[CategoryNodeModel]:
        raise NotImplementedError
    
    



