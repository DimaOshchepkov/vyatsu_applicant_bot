from typing import List, Optional

from tactic.application.common.repositories import ContestTypeRepository
from tactic.domain.entities.contest_type import ContestTypeDomain


class GetFilterdContestTypesUseCase:

    def __init__(self, contest_type_repository: ContestTypeRepository):
        self.contest_type_repository = contest_type_repository

    async def __call__(
        self,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
    ) -> List[ContestTypeDomain]:
        ids = await self.contest_type_repository.filter(
            education_level_ids=education_level_ids,
            study_form_ids=study_form_ids,
        )
        return await self.contest_type_repository.get_many(ids)
