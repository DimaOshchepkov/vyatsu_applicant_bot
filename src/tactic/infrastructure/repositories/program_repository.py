from typing import List, Optional

from sqlalchemy import or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Program, ProgramContestExam
from tactic.application.common.repositories import ProgramRepository
from tactic.domain.entities.program import (
    CreateProgramDomain,
    ProgramDomain,
    ProgramDTO,
)
from tactic.infrastructure.repositories.base_repository import BaseRepository


class ProgramRepositoryImpl(
    BaseRepository[ProgramDomain, Program, CreateProgramDomain], ProgramRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProgramDomain, Program, CreateProgramDomain)

    async def get_all_titles(self) -> List[ProgramDTO]:
        result = await self.db.execute(select(Program.id, Program.title))
        rows = result.all()

        return [ProgramDTO(id=row[0], title=row[1]) for row in rows]

    async def filter(
        self,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
        contest_type_ids: Optional[List[int]] = None,
        exam_subject_ids: Optional[List[int]] = None,
    ) -> List[int]:

        stmt = select(Program.id)

        if education_level_ids:
            stmt = stmt.where(Program.education_level_id.in_(education_level_ids))

        if study_form_ids:
            stmt = stmt.where(Program.study_form_id.in_(study_form_ids))

        if contest_type_ids:
            stmt = stmt.join(Program.contest_exams).where(
                ProgramContestExam.contest_type_id.in_(contest_type_ids)
            )

        if exam_subject_ids:
            if contest_type_ids is None:
                result = await self.db.execute(
                    select(ProgramContestExam.contest_type_id).distinct()
                )
                contest_type_ids = [row[0] for row in result.fetchall()]

            base_program_subq = stmt.with_only_columns(Program.id).subquery()

            required_missing_subq = (
                select(
                    ProgramContestExam.program_id, ProgramContestExam.contest_type_id
                )
                .where(
                    ProgramContestExam.program_id.in_(select(base_program_subq.c.id)),
                    ProgramContestExam.is_optional.is_(False),
                    ProgramContestExam.contest_type_id.in_(contest_type_ids),
                    ~ProgramContestExam.subject_id.in_(exam_subject_ids),
                )
                .distinct()
            )

            optional_match_subq = (
                select(
                    ProgramContestExam.program_id, ProgramContestExam.contest_type_id
                )
                .where(
                    ProgramContestExam.program_id.in_(select(base_program_subq.c.id)),
                    ProgramContestExam.is_optional.is_(True),
                    ProgramContestExam.contest_type_id.in_(contest_type_ids),
                    ProgramContestExam.subject_id.in_(exam_subject_ids),
                )
                .distinct()
            )

            optional_exists_subq = (
                select(
                    ProgramContestExam.program_id, ProgramContestExam.contest_type_id
                )
                .where(
                    ProgramContestExam.program_id.in_(select(base_program_subq.c.id)),
                    ProgramContestExam.is_optional.is_(True),
                    ProgramContestExam.contest_type_id.in_(contest_type_ids),
                )
                .distinct()
            )

            valid_pairs_subq = (
                select(
                    ProgramContestExam.program_id, ProgramContestExam.contest_type_id
                )
                .where(
                    ProgramContestExam.program_id.in_(select(base_program_subq.c.id)),
                    ProgramContestExam.contest_type_id.in_(contest_type_ids),
                    tuple_(
                        ProgramContestExam.program_id,
                        ProgramContestExam.contest_type_id,
                    ).not_in(required_missing_subq),
                    or_(
                        tuple_(
                            ProgramContestExam.program_id,
                            ProgramContestExam.contest_type_id,
                        ).not_in(optional_exists_subq),
                        tuple_(
                            ProgramContestExam.program_id,
                            ProgramContestExam.contest_type_id,
                        ).in_(optional_match_subq),
                    ),
                )
                .distinct()
            )

            vp_alias = valid_pairs_subq.subquery()

            stmt = select(Program.id).where(
                Program.id.in_(select(base_program_subq.c.id)),
                Program.id.in_(select(vp_alias.c.program_id)),
            )

        stmt = stmt.with_only_columns(Program.id)
        result = await self.db.execute(stmt)
        program_ids = result.scalars().all()
        return [i for i in program_ids]
