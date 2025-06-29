from typing import List, Optional

from tactic.application.common.repositories import StudyFormRepository
from tactic.domain.entities.study_form import StudyFormDomain


class GetFilterdStudyFormsUseCase:

    def __init__(self, study_form_repository: StudyFormRepository):
        self.study_form_repository = study_form_repository

    async def __call__(
        self,
        education_level_ids: Optional[List[int]] = None,
    ) -> List[StudyFormDomain]:
        ids = await self.study_form_repository.filter(
            education_level_ids=education_level_ids,
        )
        return await self.study_form_repository.get_many(ids)
