from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Protocol, Set, TypeVar

from tactic.domain.entities.category import CategoryDomain
from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.domain.entities.contest_type import ContestTypeDomain
from tactic.domain.entities.education_level import EducationLevelDomain
from tactic.domain.entities.program import ProgramDomain
from tactic.domain.entities.question import QuestionDomain
from tactic.domain.entities.study_form import StudyFormDomain
from tactic.domain.entities.subject import SubjectDomain, SubjectJsonDomain
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


class SubjectRepository(IBaseRepository[SubjectDomain], ABC):
    
    @abstractmethod
    async def filter(
        self,
        contest_type_ids: Optional[List[int]] = None,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
    ) -> List[SubjectDomain]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_eligible_program_ids(self, subject_ids: Set[int]) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    async def get_ids_by_name(self, names: Set[str]) -> Set[int]:
        raise NotImplementedError


class ProgramRepository(IBaseRepository[ProgramDomain], ABC):
    
    @abstractmethod
    async def filter(
        self,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
        contest_type_ids: Optional[List[int]] = None,
        exam_subject_ids: Optional[List[int]] = None,
    ) -> List[int]:
        raise NotImplementedError


class JsonExamRepository(ABC):

    @abstractmethod
    async def get_all(self) -> List[SubjectJsonDomain]:
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


class EducationLevelRepository(IBaseRepository[EducationLevelDomain], ABC): ...


class StudyFormRepository(IBaseRepository[StudyFormDomain], ABC): ...


class ContestTypeRepository(IBaseRepository[ContestTypeDomain], ABC): ...



