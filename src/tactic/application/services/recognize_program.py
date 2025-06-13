
from abc import ABC, abstractmethod
from typing import List

from tactic.domain.entities.program import ProgramDTO


class RecognizeProgram(ABC):
    @abstractmethod
    async def recognize(self, user_input: str, k: int = 3) -> List[ProgramDTO]:
        raise NotImplementedError