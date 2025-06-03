from typing import List

from tactic.application.common.repositories import StudyFormRepository
from tactic.domain.entities.study_form import StudyFormDomain


class GetAllStudyFormsUseCase:

    def __init__(self, study_repository: StudyFormRepository):
        self.study_repository = study_repository

    async def __call__(self) -> List[StudyFormDomain]:
        return await self.study_repository.get_all()
