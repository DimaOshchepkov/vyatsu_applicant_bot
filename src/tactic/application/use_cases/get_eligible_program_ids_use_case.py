from typing import List, Set

from tactic.application.common.repositories import SubjectRepository


class GetEligibleProgramIdsUseCase:

    def __init__(self, question_repository: SubjectRepository):
        self.exam_repository = question_repository

    async def __call__(self, exams: Set[str]) -> List[int]:
        ids = await self.exam_repository.get_ids_by_name(exams)

        return await self.exam_repository.get_eligible_program_ids(ids)
