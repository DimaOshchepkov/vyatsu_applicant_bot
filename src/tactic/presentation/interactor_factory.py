from abc import abstractmethod, ABC

from typing import AsyncContextManager

from tactic.application.create_user import CreateUser
from tactic.application.recognize_exam import RecognizeExamUseCase


class InteractorFactory(ABC):
    
    @abstractmethod
    def create_user(self) -> AsyncContextManager[CreateUser]:
        raise NotImplementedError
    
    
    @abstractmethod
    def recognize_exam(self) -> AsyncContextManager[RecognizeExamUseCase]:
        raise NotImplementedError
