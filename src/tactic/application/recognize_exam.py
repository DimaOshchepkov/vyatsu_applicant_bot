from abc import ABC, abstractmethod
from typing import List

class RecognizeExam(ABC):
    @abstractmethod
    async def recognize(self, user_input: str, k: int = 3) -> List[str]:
        pass
    
    
class RecognizeExamUseCase:
    def __init__(self, recognizer: RecognizeExam):
        self.recognizer = recognizer

    async def __call__(self, user_input: str, k: int = 3) -> List[str]:
        return await self.recognizer.recognize(user_input, k)