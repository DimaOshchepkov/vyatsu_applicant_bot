from abc import ABC, abstractmethod
from typing import List

from tactic.application.common.repositories import ProgramRepository
from tactic.application.services.recognize_exam import RecognizeExam
from tactic.application.services.recognize_program import RecognizeProgram
from tactic.domain.entities.program import ProgramDTO
from tactic.domain.entities.subject import SubjectDto


class RecognizeExamFactory(ABC):

    @abstractmethod
    async def create(self, subjects: List[SubjectDto], threshold: int) -> RecognizeExam:
        raise NotImplementedError


class RecognizeProgramFactory(ABC):

    @abstractmethod
    async def create(
        self, program_repo: ProgramRepository, threshold: int
    ) -> RecognizeProgram:
        raise NotImplementedError
