from typing import List

from tactic.application.common.fabrics import RecognizeExamFactory
from tactic.application.services.recognize_exam import RecognizeExam
from tactic.domain.entities.subject import SubjectDomain
from tactic.infrastructure.recognize_exam_rapid_wuzzy import RecognizeExamRapidWuzzy


class RecognizeExamRapidWuzzyFactory(RecognizeExamFactory):
    async def create(
        self, subjects: List[SubjectDomain], threshold: int
    ) -> RecognizeExam:
        return await RecognizeExamRapidWuzzy.create(subjects, threshold)
