from typing import Dict, List

from rapidfuzz import fuzz, process

from tactic.application.services.recognize_exam import RecognizeExam
from tactic.domain.entities.subject import SubjectDomain


class RecognizeExamFuzzywuzzy(RecognizeExam):
    def __init__(self, subject_data: List[SubjectDomain], threshold: int = 70):
        self.threshold = threshold
        self.subject_data: List[SubjectDomain] = []
        self.aliase_subject: Dict[str, List[str]] = {}
        self.exam_popularity: Dict[str, int] = {}
        self.normalized_subject_name_to_subject: Dict[str, SubjectDomain] = {}
        self.subject_data = subject_data

    @classmethod
    async def create(
        cls, subject_data: List[SubjectDomain], threshold: int = 70
    ) -> "RecognizeExamFuzzywuzzy":
        self = cls(subject_data, threshold)
        await self.setup()
        return self

    async def setup(self) -> None:
        self._build_mappings()

    def _build_mappings(self) -> None:
        """
        Строим словарь с alias (синонимами) для каждого экзамена.
        """
        for subject in self.subject_data:
            normalized_exam = subject.name.lower().strip()
            self.normalized_subject_name_to_subject[normalized_exam] = subject
            self.exam_popularity[normalized_exam] = (
                subject.popularity if subject.popularity else 0
            )

            aliases_name = [a.alias for a in subject.aliases]
            for word in [subject.name] + aliases_name:
                normalized = word.lower().strip()
                if normalized not in self.aliase_subject:
                    self.aliase_subject[normalized] = [normalized_exam]
                else:
                    self.aliase_subject[normalized].append(normalized_exam)

    async def recognize(self, user_input: str, k: int = 3) -> List[SubjectDomain]:
        def unique_elements(seq):
            return list(dict.fromkeys(seq))

        user_input = user_input.lower().strip()

        matches = process.extract(
            user_input,
            self.aliase_subject.keys(),
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
            matched_exams.extend(self.aliase_subject[alias])

        normalized_matched = unique_elements(matched_exams)[:k]

        return [
            self.normalized_subject_name_to_subject[ex] for ex in normalized_matched
        ]

    def get_popularity(self, exam_name: str) -> int:
        return self.exam_popularity.get(exam_name.lower(), 0)
