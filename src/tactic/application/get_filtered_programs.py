from typing import List, Optional

from tactic.application.common.repositories import ProgramRepository


class GetFilterdProgramsUseCase:

    def __init__(self, program_repository: ProgramRepository):
        self.program_repository = program_repository

    async def __call__(
        self,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
        contest_type_ids: Optional[List[int]] = None,
        exam_subject_ids: Optional[List[int]] = None,
    ) -> List[int]:
        return await self.program_repository.filter_programs(
            education_level_ids=education_level_ids,
            study_form_ids=study_form_ids,
            contest_type_ids=contest_type_ids,
            exam_subject_ids=exam_subject_ids,
        )
