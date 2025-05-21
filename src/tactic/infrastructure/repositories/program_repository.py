from typing import Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Program
from tactic.application.common.repositories import ProgramRepository
from tactic.domain.entities.program import ProgramDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository


class ProgramRepositoryImpl(BaseRepository[ProgramDomain, Program], ProgramRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProgramDomain, Program)


