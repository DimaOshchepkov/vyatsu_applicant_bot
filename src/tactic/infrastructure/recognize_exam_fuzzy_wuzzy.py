from tactic.application.common.repositories import ExamRepository
from tactic.application.recognize_exam import RecognizeExam
from rapidfuzz import fuzz, process
from typing import List, Dict

from tactic.domain.entities.exam import Exam


class RecognizeExamFuzzywuzzy(RecognizeExam):
    def __init__(
        self,
        exam_repository: ExamRepository,
        threshold: int = 70
    ):
        self.threshold = threshold
        self.exam_repository = exam_repository
        self.exam_data: List[Exam] = []
        self.aliase_exams: Dict[str, List[str]] = {}
        self.exam_popularity: Dict[str, int] = {}

    @classmethod
    async def create(cls, exam_repository: ExamRepository, threshold: int = 70) -> "RecognizeExamFuzzywuzzy":
        self = cls(exam_repository, threshold)
        await self.setup()
        return self

    async def setup(self) -> None:
        self.exam_data = await self.exam_repository.get_all()
        self._build_mappings()

    def _build_mappings(self) -> None:
        """
        Строим словарь с alias (синонимами) для каждого экзамена.
        """
        for info in self.exam_data:
            normalized_exam = info.exam.lower().strip()
            self.exam_popularity[normalized_exam] = info.popularity

            for word in [info.exam] + info.aliases:
                normalized = word.lower().strip()
                if normalized not in self.aliase_exams:
                    self.aliase_exams[normalized] = [normalized_exam]
                else:
                    self.aliase_exams[normalized].append(normalized_exam)

    async def recognize(self, user_input: str, k: int = 3) -> List[str]:
        def unique_elements(seq):
            return list(dict.fromkeys(seq))

        user_input = user_input.lower().strip()

        matches = process.extract(
            user_input,
            self.aliase_exams.keys(),
            scorer=fuzz.ratio,
            limit=k,
            score_cutoff=self.threshold,  # Это отличие rapidfuzz: можно сразу порог указать
        )

        # В rapidfuzz результат немного другой: [(key, score, index)], нам нужен key и score
        filtered = [(alias, score) for alias, score, _ in matches]
        filtered.sort(key=lambda x: (-x[1], -self.get_popularity(x[0])))

        if not filtered:
            return []

        matched_exams = []
        for alias, _ in filtered:
            matched_exams.extend(self.aliase_exams[alias])

        return unique_elements(matched_exams)[:k]

    def get_popularity(self, exam_name: str) -> int:
        return self.exam_popularity.get(exam_name.lower(), 0)