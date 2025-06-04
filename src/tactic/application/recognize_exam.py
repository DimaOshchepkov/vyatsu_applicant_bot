from abc import ABC, abstractmethod
from typing import List

from tactic.domain.entities.subject import SubjectDomain

class RecognizeExam(ABC):
    @abstractmethod
    async def recognize(self, user_input: str, k: int = 3) -> List[SubjectDomain]:
        pass
    
    
class RecognizeExamUseCase:
    def __init__(self, recognizer: RecognizeExam):
        self.recognizer = recognizer

    async def __call__(self, user_input: str, k: int = 3) -> List[SubjectDomain]:
        return await self.recognizer.recognize(user_input, k)