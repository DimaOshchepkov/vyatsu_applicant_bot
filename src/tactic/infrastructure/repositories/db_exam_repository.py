from typing import List, Set

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Program, ProgramContestExam, Subject
from tactic.application.common.repositories import ExamRepository
from tactic.domain.entities.exam import ExamDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository


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

        # Подзапрос: общее количество обязательных экзаменов на каждую программу
        required_subq = (
            select(ProgramContestExam.program_id, func.count().label("required_count"))
            .where(ProgramContestExam.is_optional.is_(False))
            .group_by(ProgramContestExam.program_id)
            .subquery()
        )

        # Подзапрос: количество обязательных экзаменов, которые пользователь сдал
        user_required_subq = (
            select(
                ProgramContestExam.program_id, func.count().label("user_required_count")
            )
            .where(
                ProgramContestExam.is_optional.is_(False),
                ProgramContestExam.subject_id.in_(subject_ids),
            )
            .group_by(ProgramContestExam.program_id)
            .subquery()
        )

        # Подзапрос: есть ли хотя бы один подходящий опциональный экзамен
        optional_exists_subq = (
            select(ProgramContestExam.program_id)
            .where(
                ProgramContestExam.is_optional.is_(True),
                ProgramContestExam.subject_id.in_(subject_ids),
            )
            .distinct()
            .subquery()
        )

        # Подзапрос: проверка, есть ли вообще опциональные экзамены
        optional_count_subq = (
            select(ProgramContestExam.program_id, func.count().label("optional_count"))
            .where(ProgramContestExam.is_optional.is_(True))
            .group_by(ProgramContestExam.program_id)
            .subquery()
        )

        # Объединяем всё
        stmt = (
            select(Program.id)
            .join(required_subq, Program.id == required_subq.c.program_id)
            .join(user_required_subq, Program.id == user_required_subq.c.program_id)
            .outerjoin(
                optional_count_subq, Program.id == optional_count_subq.c.program_id
            )
            .outerjoin(
                optional_exists_subq, Program.id == optional_exists_subq.c.program_id
            )
            .where(
                # Все обязательные экзамены сданы
                required_subq.c.required_count
                >= user_required_subq.c.user_required_count,
                # И (либо нет опциональных, либо хотя бы один подошёл)
                case(
                    (optional_count_subq.c.optional_count.is_(None), True),
                    (optional_exists_subq.c.program_id.is_not(None), True),
                    else_=False,
                ),
            )
        )

        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]
