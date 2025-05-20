from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Protocol, Set, TypeVar

from tactic.domain.entities.category import CategoryDomain
from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.domain.entities.exam import ExamDomain, ExamJsonDomain
from tactic.domain.entities.question import QuestionDomain
from tactic.domain.entities.user import User
from tactic.domain.value_objects.user import UserId

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


class ExamRepository(IBaseRepository[ExamDomain], ABC):

    @abstractmethod
    async def get_eligible_program_ids(self, subject_ids: Set[int]) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    async def get_ids_by_name(self, names: Set[str]) -> Set[int]:
        raise NotImplementedError
    
class JsonExamRepository(ABC):

    @abstractmethod
    async def get_all(self) -> List[ExamJsonDomain]:
        raise NotImplementedError


class CategoryRepository(IBaseRepository[CategoryDomain], ABC):

    @abstractmethod
    async def get_category_tree(self) -> List[CategoryNodeModel]:
        raise NotImplementedError


class QuestionRepository(IBaseRepository[QuestionDomain], ABC):

    @abstractmethod
    async def get_questions_by_category_id(
        self, category_id: int
    ) -> List[QuestionDomain]:
        raise NotImplementedError
