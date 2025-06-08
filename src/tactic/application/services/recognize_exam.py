from abc import ABC, abstractmethod
from typing import List

from tactic.domain.entities.subject import SubjectDomain


class RecognizeExam(ABC):
    @abstractmethod
    async def recognize(self, user_input: str, k: int = 3) -> List[SubjectDomain]:
        raise NotImplementedError
