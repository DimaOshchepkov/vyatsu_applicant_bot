from typing import List

from tactic.application.services.recognize_program import RecognizeProgram
from tactic.domain.entities.program import ProgramDTO


class RecognizeProgramUseCase:
    def __init__(
        self,
        recognize_program: RecognizeProgram,
    ):
        self.recognize_program = recognize_program

    async def __call__(
        self,
        user_input: str,
        k: int = 3,
    ) -> List[ProgramDTO]:

        return await self.recognize_program.recognize(user_input, k)
