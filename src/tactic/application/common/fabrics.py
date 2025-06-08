
from abc import ABC, abstractmethod
from typing import List

from tactic.application.services.recognize_exam import RecognizeExam
from tactic.domain.entities.subject import SubjectDomain


class RecognizeExamFactory(ABC):
    
    @abstractmethod
    async def create(self, subjects: List[SubjectDomain], threshold: int) -> RecognizeExam:
        raise NotImplementedError
