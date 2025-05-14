from abc import abstractmethod, ABC

from typing import AsyncContextManager

from tactic.application.create_user import CreateUser
from tactic.application.get_categories import GetCategoriesUseCase
from tactic.application.get_questions import GetQuestionsUseCase
from tactic.application.get_questions_by_category_id import GetQuestionsByCategoryIdUseCase
from tactic.application.get_questions_category_tree import GetQuestionsCategoryTreeUseCase
from tactic.application.recognize_exam import RecognizeExamUseCase


class InteractorFactory(ABC):
    
    @abstractmethod
    def create_user(self) -> AsyncContextManager[CreateUser]:
        raise NotImplementedError

    @abstractmethod
    def recognize_exam(self) -> AsyncContextManager[RecognizeExamUseCase]:
        raise NotImplementedError
    
    @abstractmethod
    def get_questions_category(self) -> AsyncContextManager[GetQuestionsCategoryTreeUseCase]:
        raise NotImplementedError
    
    @abstractmethod
    def get_categories(self) -> AsyncContextManager[GetCategoriesUseCase]:
        raise NotImplementedError
    
    @abstractmethod
    def get_questions(self) -> AsyncContextManager[GetQuestionsUseCase]:
        raise NotImplementedError
    
    @abstractmethod
    def get_questions_by_category_id(self) -> AsyncContextManager[GetQuestionsByCategoryIdUseCase]:
        raise NotImplementedError
