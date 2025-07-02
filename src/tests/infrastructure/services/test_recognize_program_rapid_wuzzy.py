from typing import List
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from tactic.domain.entities.program import ProgramDTO
from tactic.infrastructure.recognize_program_rapid_wuzzy import (
    RecognizeProgramRapidWuzzy,
)



@pytest_asyncio.fixture
async def recognizer():
    programs = [
        ProgramDTO(id=1, title="Прикладная информатика"),
        ProgramDTO(id=2, title="Фундаментальная математика"),
        ProgramDTO(id=3, title="Программная инженерия"),
        ProgramDTO(id=4, title="Бизнес-информатика"),
    ]
    return await RecognizeProgramRapidWuzzy.create(programs=programs, threshold=70)


@pytest.mark.asyncio
async def test_exact_match(recognizer: RecognizeProgramRapidWuzzy):
    result = await recognizer.recognize("Программная инженерия")
    assert len(result) == 1
    assert result[0].title == "Программная инженерия"


@pytest.mark.asyncio
async def test_fuzzy_match(recognizer: RecognizeProgramRapidWuzzy):
    result = await recognizer.recognize("прикладная инфа")
    assert result
    titles = [r.title for r in result]
    assert any("Прикладная информатика" in t for t in titles)


@pytest.mark.asyncio
async def test_case_and_whitespace_insensitivity(
    recognizer: RecognizeProgramRapidWuzzy,
):
    result = await recognizer.recognize("   бизнес-ИНФОРМАТИКА ")
    assert result
    assert result[0].title == "Бизнес-информатика"


@pytest.mark.asyncio
async def test_threshold_blocks_low_score():
    programs = [ProgramDTO(id=5, title="История искусств")]
    recognizer = await RecognizeProgramRapidWuzzy.create(programs, threshold=90)

    result = await recognizer.recognize("искусств")
    assert result == []


@pytest.mark.asyncio
async def test_limit_k(recognizer: RecognizeProgramRapidWuzzy):
    result = await recognizer.recognize("информатика", k=2)
    # В названиях 2+ программ с этим словом, но мы ограничиваем до 2
    assert len(result) <= 2
    titles = [p.title for p in result]
    assert any("информатика" in t.lower() for t in titles)
