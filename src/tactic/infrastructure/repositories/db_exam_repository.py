import logging
from typing import List, Set

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from shared.models import ProgramContestExam, Subject
from tactic.application.common.repositories import ExamRepository
from tactic.domain.entities.exam import ExamDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DbExamRepository(BaseRepository[ExamDomain, Subject], ExamRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ExamDomain, Subject)

    async def get_ids_by_name(self, names: Set[str]) -> Set[int]:
        if not names:
            return set()

        stmt = select(Subject.id).where(Subject.name.in_(names))
        result = await self.db.execute(stmt)
        ids = result.scalars().all()
        return set(ids)

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
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        logger.info(str(eligible_pairs_stmt))
        logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        result = await self.db.execute(eligible_pairs_stmt)
        return list({row[0] for row in result.all()})  # уникальные program_id
