import json
from pathlib import Path
from typing import List, Set

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Subject
from tactic.application.common.repositories import ExamRepository, JsonExamRepository
from tactic.domain.entities.exam import ExamJsonDomain
from tactic.infrastructure.repositories.base_repository import BaseRepository


class JsonExamRepositoryImpl(JsonExamRepository):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    async def get_all(self) -> List[ExamJsonDomain]:
        async with aiofiles.open(self.file_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)
        return [ExamJsonDomain(**item) for item in data]

    async def get_eligible_program_ids(self, subject_ids: Set[int]) -> List[int]:
        raise NotImplementedError

    async def get_ids_by_name(self, names: Set[str]) -> Set[int]:
        raise NotImplementedError
