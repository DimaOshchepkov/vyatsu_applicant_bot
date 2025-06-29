from typing import List, Optional

from tactic.application.common.fabrics import RecognizeExamFactory
from tactic.application.common.repositories import SubjectRepository
from tactic.domain.entities.subject import SubjectDto


class RecognizeExamUseCase:
    def __init__(
        self,
        subj_repo: SubjectRepository,
        recognizer_factory: RecognizeExamFactory,
    ):
        self.subj_repo = subj_repo
        self.recognizer_factory = recognizer_factory

    async def __call__(
        self,
        user_input: str,
        k: int = 3,
        threshold: int = 70,
        contest_type_ids: Optional[List[int]] = None,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
    ) -> List[SubjectDto]:
        subjects = await self.subj_repo.filter(
            contest_type_ids=contest_type_ids,
            education_level_ids=education_level_ids,
            study_form_ids=study_form_ids,
        )
        recognizer = await self.recognizer_factory.create(subjects, threshold)
        return await recognizer.recognize(user_input, k)
