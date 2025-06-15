from typing import List

from aiocache import cached
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import StudyForm
from tactic.application.common.repositories import StudyFormRepository
from tactic.domain.entities.study_form import CreateStudyFormDomain, StudyFormDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository
from tactic.infrastructure.repositories.cache_config import classaware_key_builder


class StudyFormRepositoryImpl(
    BaseRepository[StudyFormDomain, StudyForm, CreateStudyFormDomain],
    StudyFormRepository,
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, StudyFormDomain, StudyForm, CreateStudyFormDomain)

    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[StudyFormDomain]: #type: ignore
        return await super().get_all()
