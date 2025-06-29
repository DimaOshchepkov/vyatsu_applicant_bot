import logging
from typing import List, Optional

from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import Program, ProgramContestExam, Subject
from tactic.application.common.repositories import SubjectRepository
from tactic.domain.entities.subject import (
    CreateSubjectDomain,
    SubjectAliasDomain,
    SubjectDomain,
    SubjectDto,
)
from tactic.infrastructure.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DbSubjectRepository(
    BaseRepository[SubjectDomain, Subject, CreateSubjectDomain], SubjectRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SubjectDomain, Subject, CreateSubjectDomain)

    async def filter(
        self,
        contest_type_ids: Optional[List[int]] = None,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
    ) -> List[SubjectDto]:

        stmt = select(Subject).distinct()
        stmt = stmt.join(ProgramContestExam, Subject.contest_exams).options(
            selectinload(Subject.aliases)
        )

        if contest_type_ids:
            stmt = stmt.where(ProgramContestExam.contest_type_id.in_(contest_type_ids))

        if education_level_ids or study_form_ids:
            stmt = stmt.join(Program, ProgramContestExam.program)

            if education_level_ids:
                stmt = stmt.where(Program.education_level_id.in_(education_level_ids))

            if study_form_ids:
                stmt = stmt.where(Program.study_form_id.in_(study_form_ids))

        result = await self.db.execute(stmt)
        return [self.to_subject_dto(m) for m in result.scalars().all()]

    def to_subject_dto(self, orm_obj: Subject) -> SubjectDto:
        return SubjectDto(
            id=orm_obj.id,
            name=orm_obj.name,
            popularity=orm_obj.popularity,
            aliases=[
                SubjectAliasDomain(
                    id=alias.id, alias=alias.alias, subject_id=alias.subject_id
                )
                for alias in orm_obj.aliases
            ],
        )
