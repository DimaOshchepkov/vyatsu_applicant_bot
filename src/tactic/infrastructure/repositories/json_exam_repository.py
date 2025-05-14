import json
from pathlib import Path
from typing import List

import aiofiles

from tactic.application.common.repositories import ExamRepository
from tactic.domain.entities.exam import Exam


class JsonExamRepository(ExamRepository):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    async def get_all(self) -> List[Exam]:
        async with aiofiles.open(self.file_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
        return [Exam(**item) for item in data]