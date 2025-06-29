from abc import ABC, abstractmethod
from typing import AsyncContextManager

from tactic.application.services.recognize_program import RecognizeProgram
from tactic.application.use_cases.create_user import CreateUser
from tactic.application.use_cases.get_all_contest_types import GetAllContestTypesUseCase
from tactic.application.use_cases.get_all_education_levels import (
    GetAllEducationLevelsUseCase,
)
from tactic.application.use_cases.get_all_study_forms import GetAllStudyFormsUseCase
from tactic.application.use_cases.get_categories import GetCategoriesUseCase
from tactic.application.use_cases.get_eligible_program_ids_use_case import (
    GetEligibleProgramIdsUseCase,
)
from tactic.application.use_cases.get_filtered_contest_type import GetFilterdContestTypesUseCase
from tactic.application.use_cases.get_filtered_programs import GetFilterdProgramsUseCase
from tactic.application.use_cases.get_filtered_study_forms import GetFilterdStudyFormsUseCase
from tactic.application.use_cases.get_list_subsriptions import (
    GetListSubscriptionsUseCase,
)
from tactic.application.use_cases.get_questions import GetQuestionsUseCase
from tactic.application.use_cases.get_questions_by_category_id import (
    GetQuestionsByCategoryIdUseCase,
)
from tactic.application.use_cases.get_questions_category_tree import (
    GetQuestionsCategoryTreeUseCase,
)
from tactic.application.use_cases.get_sheduled_notification_by_subscription import (
    GetScheduledNotificationsBySubscriptionUseCase,
)
from tactic.application.use_cases.get_timeline_event import GetTimelineEventUseCase
from tactic.application.use_cases.recognize_exam import RecognizeExamUseCase
from tactic.application.use_cases.recognize_program import RecognizeProgramUseCase
from tactic.application.use_cases.send_notification import SendNotificationUseCase
from tactic.application.use_cases.subscribe_for_program import (
    SubscribeForProgramUseCase,
)
from tactic.application.use_cases.unsubscrib_from_program import (
    UnsubscribeFromProgramUseCase,
)
from tactic.infrastructure.telegram.rate_limited_bot import RateLimitedBot


class InteractorFactory(ABC):

    @abstractmethod
    def create_user(self) -> AsyncContextManager[CreateUser]:
        raise NotImplementedError

    @abstractmethod
    def recognize_exam(self) -> AsyncContextManager[RecognizeExamUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_questions_category(
        self,
    ) -> AsyncContextManager[GetQuestionsCategoryTreeUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_categories(self) -> AsyncContextManager[GetCategoriesUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_questions(self) -> AsyncContextManager[GetQuestionsUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_questions_by_category_id(
        self,
    ) -> AsyncContextManager[GetQuestionsByCategoryIdUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_eligible_program_ids(
        self,
    ) -> AsyncContextManager[GetEligibleProgramIdsUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_all_education_levels(
        self,
    ) -> AsyncContextManager[GetAllEducationLevelsUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_all_study_forms(self) -> AsyncContextManager[GetAllStudyFormsUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_all_contest_types(self) -> AsyncContextManager[GetAllContestTypesUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_filtered_programs(self) -> AsyncContextManager[GetFilterdProgramsUseCase]:
        raise NotImplementedError

    @abstractmethod
    def send_telegram_notification(
        self,
    ) -> AsyncContextManager[SendNotificationUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_timeline_events(self) -> AsyncContextManager[GetTimelineEventUseCase]:
        raise NotImplementedError

    @abstractmethod
    def recognize_program(self) -> AsyncContextManager[RecognizeProgramUseCase]:
        raise NotImplementedError

    @abstractmethod
    def subscribe_for_program(self) -> AsyncContextManager[SubscribeForProgramUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_list_subscriptions(
        self,
    ) -> AsyncContextManager[GetListSubscriptionsUseCase]:
        raise NotImplementedError

    @abstractmethod
    def unsubscribe_from_program(
        self,
    ) -> AsyncContextManager[UnsubscribeFromProgramUseCase]:
        raise NotImplementedError

    @abstractmethod
    def get_sheduled_notification(
        self,
    ) -> AsyncContextManager[GetScheduledNotificationsBySubscriptionUseCase]:
        raise NotImplementedError
    
    @abstractmethod
    def get_filtered_study_forms(self) -> AsyncContextManager[GetFilterdStudyFormsUseCase]:
        raise NotImplementedError
    
    @abstractmethod
    def get_filtered_contest_types(self) -> AsyncContextManager[GetFilterdContestTypesUseCase]:
        raise NotImplementedError
