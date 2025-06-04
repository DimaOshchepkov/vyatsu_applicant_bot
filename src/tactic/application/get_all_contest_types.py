from typing import List
from tactic.application.common.repositories import ContestTypeRepository
from tactic.domain.entities.contest_type import ContestTypeDomain


class GetAllContestTypesUseCase:

    def __init__(self, contest_type_repository: ContestTypeRepository):
        self.contest_type_repository = contest_type_repository

    async def __call__(self) -> List[ContestTypeDomain]:
        return await self.contest_type_repository.get_all()