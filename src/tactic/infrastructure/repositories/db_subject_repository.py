import logging
from typing import Collection, List, Optional, Sequence, Set

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import Program, ProgramContestExam, Subject, SubjectAlias
from tactic.application.common.repositories import SubjectRepository
from tactic.domain.entities.subject import (
    CreateSubjectDomain,
    SubjectAliasDomain,
    SubjectDomain,
)
from tactic.infrastructure.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DbSubjectRepository(
    SubjectRepository
):  # TODO: Стоит ввести SubjectDto вместо SubjectDomain, чтобы не терять функционал базового класса
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[SubjectDomain]:
        raise NotImplementedError
    
    async def get_many(self, ids: Collection[int]) -> List[SubjectDomain]:
        raise NotImplementedError

    async def add(self, create_dto: CreateSubjectDomain) -> SubjectDomain:
        raise NotImplementedError

    async def add_all(
        self, create_dtos: Sequence[CreateSubjectDomain]
    ) -> List[SubjectDomain]:
        raise NotImplementedError

    async def update(self, entity: SubjectDomain) -> SubjectDomain:
        raise NotImplementedError

    async def delete(self, id: int) -> None:
        raise NotImplementedError

    async def delete_all(self, ids: List[int]) -> None:
        raise NotImplementedError
    
    async def get_ids_by_name(self, names: Set[str]) -> Set[int]:
        if not names:
            return set()

        stmt = select(Subject.id).where(Subject.name.in_(names))
        result = await self.db.execute(stmt)
        ids = result.scalars().all()
        return set(ids)

    async def filter(
        self,
        contest_type_ids: Optional[List[int]] = None,
        education_level_ids: Optional[List[int]] = None,
        study_form_ids: Optional[List[int]] = None,
    ) -> List[SubjectDomain]:

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
        return [self.to_domain(m) for m in result.scalars().all()]

    async def get_eligible_program_ids(self, subject_ids: Set[int]) -> List[int]:
        if not subject_ids:
            return []

        # Все существующие пары (program_id, contest_type_id), у которых вообще есть экзамены
        existing_pairs_subq = (
            select(ProgramContestExam.program_id, ProgramContestExam.contest_type_id)
            .distinct()
            .subquery()
        )

        # Обязательные экзамены по каждой паре (program_id, contest_type_id)
        required_subq = (
            select(
                ProgramContestExam.program_id,
                ProgramContestExam.contest_type_id,
                func.count().label("required_count"),
            )
            .where(ProgramContestExam.is_optional.is_(False))
            .group_by(ProgramContestExam.program_id, ProgramContestExam.contest_type_id)
            .subquery()
        )

        # Сданные обязательные экзамены абитуриентом
        user_required_subq = (
            select(
                ProgramContestExam.program_id,
                ProgramContestExam.contest_type_id,
                func.count().label("user_required_count"),
            )
            .where(
                ProgramContestExam.is_optional.is_(False),
                ProgramContestExam.subject_id.in_(subject_ids),
            )
            .group_by(ProgramContestExam.program_id, ProgramContestExam.contest_type_id)
            .subquery()
        )

        # Опциональные экзамены, которые сдал пользователь
        user_optional_subq = (
            select(ProgramContestExam.program_id, ProgramContestExam.contest_type_id)
            .where(
                ProgramContestExam.is_optional.is_(True),
                ProgramContestExam.subject_id.in_(subject_ids),
            )
            .distinct()
            .subquery()
        )

        # Есть ли вообще опциональные экзамены
        optional_exists_subq = (
            select(
                ProgramContestExam.program_id,
                ProgramContestExam.contest_type_id,
                func.count().label("optional_count"),
            )
            .where(ProgramContestExam.is_optional.is_(True))
            .group_by(ProgramContestExam.program_id, ProgramContestExam.contest_type_id)
            .subquery()
        )

        # Собираем: только те пары, где выполнены все условия
        eligible_pairs_stmt = (
            select(existing_pairs_subq.c.program_id)
            .select_from(existing_pairs_subq)
            .join(
                required_subq,
                and_(
                    existing_pairs_subq.c.program_id == required_subq.c.program_id,
                    existing_pairs_subq.c.contest_type_id
                    == required_subq.c.contest_type_id,
                ),
                isouter=True,
            )
            .join(
                user_required_subq,
                and_(
                    existing_pairs_subq.c.program_id == user_required_subq.c.program_id,
                    existing_pairs_subq.c.contest_type_id
                    == user_required_subq.c.contest_type_id,
                ),
                isouter=True,
            )
            .join(
                optional_exists_subq,
                and_(
                    existing_pairs_subq.c.program_id
                    == optional_exists_subq.c.program_id,
                    existing_pairs_subq.c.contest_type_id
                    == optional_exists_subq.c.contest_type_id,
                ),
                isouter=True,
            )
            .join(
                user_optional_subq,
                and_(
                    existing_pairs_subq.c.program_id == user_optional_subq.c.program_id,
                    existing_pairs_subq.c.contest_type_id
                    == user_optional_subq.c.contest_type_id,
                ),
                isouter=True,
            )
            .where(
                # Все обязательные экзамены сданы
                or_(
                    required_subq.c.required_count.is_(
                        None
                    ),  # нет обязательных экзаменов
                    required_subq.c.required_count
                    == user_required_subq.c.user_required_count,
                ),
                # Если есть опциональные — хотя бы один должен быть сдан
                or_(
                    optional_exists_subq.c.optional_count.is_(None),
                    user_optional_subq.c.contest_type_id.is_not(None),
                ),
            )
            .distinct()
        )
        logger.info(
            "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        )
        logger.info(str(eligible_pairs_stmt))
        logger.info(
            "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        )

        result = await self.db.execute(eligible_pairs_stmt)
        return list({row[0] for row in result.all()})  # уникальные program_id

    async def get_all(self) -> List[SubjectDomain]:
        stmt = select(Subject).options(selectinload(Subject.aliases))
        result = await self.db.execute(stmt)
        objs = result.scalars().all()
        return [self.to_domain(obj) for obj in objs]

    def to_orm(self, domain_obj: SubjectDomain) -> Subject:
        return Subject(
            id=domain_obj.id,
            name=domain_obj.name,
            popularity=domain_obj.popularity,
            aliases=[
                SubjectAlias(id=alias.id, alias=alias.alias, subject_id=domain_obj.id)
                for alias in domain_obj.aliases
            ],
        )

    def to_domain(self, orm_obj: Subject) -> SubjectDomain:
        return SubjectDomain(
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
