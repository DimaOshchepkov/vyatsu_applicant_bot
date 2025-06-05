from typing import List

from tactic.application.common.repositories import EducationLevelRepository
from tactic.domain.entities.education_level import EducationLevelDomain


class GetAllEducationLevelsUseCase:

    def __init__(self, education_repository: EducationLevelRepository):
        self.education_repository = education_repository

    async def __call__(self) -> List[EducationLevelDomain]:
        return await self.education_repository.get_all()
