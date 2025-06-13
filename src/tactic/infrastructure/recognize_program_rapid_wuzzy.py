from typing import Dict, List, Optional

from rapidfuzz import fuzz, process

from tactic.application.services.recognize_program import RecognizeProgram
from tactic.domain.entities.program import ProgramDTO


class RecognizeProgramRapidWuzzy(RecognizeProgram):
    def __init__(self, programs: List[ProgramDTO], threshold: Optional[int] = 70):
        self.threshold = threshold
        self.programs = programs

        # Предобработанные названия
        self.normalized_titles: List[str] = []
        self.title_to_program: Dict[str, ProgramDTO] = {}

    async def _build_index(self) -> None:
        self.normalized_titles = []
        for program in self.programs:
            normalized_title = program.title.lower().strip()
            self.normalized_titles.append(normalized_title)
            self.title_to_program[normalized_title] = program

    @classmethod
    async def create(
        cls, programs: List[ProgramDTO], threshold: Optional[int] = 70
    ) -> "RecognizeProgramRapidWuzzy":
        self = cls(programs, threshold)
        await self._build_index()
        return self

    async def recognize(self, user_input: str, k: int = 5) -> List[ProgramDTO]:
        input_normalized = user_input.lower().strip()

        matches = process.extract(
            input_normalized,
            self.normalized_titles,
            scorer=fuzz.ratio,
            limit=k,
            score_cutoff=self.threshold,
        )

        # matches: List[Tuple[str, score, index]]
        sorted_titles = [title for title, score, _ in matches]

        return [self.title_to_program[title] for title in sorted_titles]
