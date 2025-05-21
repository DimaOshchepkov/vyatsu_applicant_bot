import json
from pathlib import Path
from typing import List

import aiofiles

from tactic.application.common.repositories import JsonExamRepository
from tactic.domain.entities.exam import ExamJsonDomain
from sqlalchemy.ext.asyncio import AsyncSession



class JsonExamRepositoryImpl(JsonExamRepository):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    async def get_all(self) -> List[ExamJsonDomain]:
        async with aiofiles.open(self.file_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)
        return [ExamJsonDomain(**item) for item in data]


