from abc import ABC, abstractmethod
from typing import Collection, Generic, List, Optional, Protocol, Sequence, Set, TypeVar

from shared.models import TimelineEventName
from tactic.domain.entities.category import CategoryDomain, CreateCategoryDomain
from tactic.domain.entities.category_node_model import CategoryNodeModel
from tactic.domain.entities.contest_type import (
    ContestTypeDomain,
    CreateContestTypeDomain,
)
from tactic.domain.entities.education_level import (
    CreateEducationLevelDomain,
    EducationLevelDomain,
)
from tactic.domain.entities.notification_subscription import (
    CreateNotificationSubscriptionDomain,
    NotificationSubscriptionDomain,
)
from tactic.domain.entities.program import (
    CreateProgramDomain,
    ProgramDomain,
    ProgramDTO,
)
from tactic.domain.entities.question import CreateQuestionDomain, QuestionDomain
from tactic.domain.entities.sheduled_notification import (
    CreateScheduledNotificationDomain,
    ScheduledNotificationDomain,
)
from tactic.domain.entities.study_form import CreateStudyFormDomain, StudyFormDomain
from tactic.domain.entities.subject import (
    CreateSubjectDomain,
    SubjectDomain,
    SubjectJsonDomain,
)
from tactic.domain.entities.timeline_event import (
    CreateTimelineEventDomain,
    TimelineEventDomain,
    TimelineEventDTO,
)
from tactic.domain.entities.timeline_event_name import (
    CreateTimelineEventNameDomain,
    TimelineEventNameDomain,
)
from tactic.domain.entities.timeline_type import (
    CreateTimelineTypeDomain,
    TimelineTypeDomain,
)
from tactic.domain.entities.user import User
from tactic.domain.value_objects.user import UserId

T = TypeVar("T")  # доменная модель
TCreate = TypeVar("TCreate")


class IBaseRepository(ABC, Generic[T, TCreate]):

    @abstractmethod
    async def get(self, id: int) -> Optional[T]: ...

    @abstractmethod
    async def get_all(self) -> List[T]: ...

    @abstractmethod
    async def add(self, create_dto: TCreate) -> T: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, id: int) -> None: ...

    @abstractmethod
    async def delete_all(self, ids: List[int]) -> None: ...

    @abstractmethod
    async def add_all(self, create_dtos: Sequence[TCreate]) -> List[T]: ...

    @abstractmethod
    async def get_many(self, ids: Collection[int]) -> List[T]: ...


class UserRepository(Protocol):
    """User repository interface"""

    async def create(self, user: User) -> User:
        raise NotImplementedError

    async def exists(self, user_id: UserId) -> bool:
        raise NotImplementedError


class SubjectRepository(IBaseRepository[SubjectDomain, CreateSubjectDomain], ABC):

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


class ProgramRepository(IBaseRepository[ProgramDomain, CreateProgramDomain], ABC):

    @abstractmethod
    async def filter(
        self,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
        contest_type_ids: Optional[List[int]] = None,
        exam_subject_ids: Optional[List[int]] = None,
    ) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_titles(self) -> List[ProgramDTO]:
        raise NotImplementedError


class JsonExamRepository(ABC):

    @abstractmethod
    async def get_all(self) -> List[SubjectJsonDomain]:
        raise NotImplementedError


class CategoryRepository(IBaseRepository[CategoryDomain, CreateCategoryDomain], ABC):

    @abstractmethod
    async def get_category_tree(self) -> List[CategoryNodeModel]:
        raise NotImplementedError


class QuestionRepository(IBaseRepository[QuestionDomain, CreateQuestionDomain], ABC):

    @abstractmethod
    async def get_questions_by_category_id(
        self, category_id: int
    ) -> List[QuestionDomain]:
        raise NotImplementedError


class EducationLevelRepository(
    IBaseRepository[EducationLevelDomain, CreateEducationLevelDomain], ABC
): ...


class StudyFormRepository(
    IBaseRepository[StudyFormDomain, CreateStudyFormDomain], ABC
): ...


class ContestTypeRepository(
    IBaseRepository[ContestTypeDomain, CreateContestTypeDomain], ABC
): ...


class TimelineEventRepository(
    IBaseRepository[TimelineEventDomain, CreateTimelineEventDomain], ABC
):

    @abstractmethod
    async def filter(
        self, program_id: int | None, timeline_type_id: int | None
    ) -> List[TimelineEventDTO]:
        raise NotImplementedError


class ScheduledNotificationRepository(
    IBaseRepository[ScheduledNotificationDomain, CreateScheduledNotificationDomain], ABC
):
    @abstractmethod
    async def filter(
        self, notification_subscription_id: Optional[int] = None
    ) -> List[ScheduledNotificationDomain]:
        raise NotImplementedError


class NotificationSubscriptionRepository(
    IBaseRepository[
        NotificationSubscriptionDomain, CreateNotificationSubscriptionDomain
    ],
    ABC,
):
    @abstractmethod
    async def filter(
        self,
        user_id: Optional[int] = None,
        program_id: Optional[int] = None,
        timeline_type_id: Optional[int] = None,
    ) -> List[NotificationSubscriptionDomain]:
        raise NotImplementedError


class TimelineTypeRepository(
    IBaseRepository[TimelineTypeDomain, CreateTimelineTypeDomain], ABC
): ...


class TimelineEventNameRepository(
    IBaseRepository[TimelineEventNameDomain, CreateTimelineEventNameDomain], ABC
): ...
