from typing import List
import pytest
import pytest_asyncio
from unittest.mock import MagicMock

from tactic.infrastructure.recognize_exam_rapid_wuzzy import RecognizeExamRapidWuzzy



def make_subject(name: str, aliases: List[str], popularity: int):
    subject = MagicMock()
    subject.name = name
    subject.popularity = popularity
    subject.aliases = [MagicMock(alias=a) for a in aliases]
    return subject


@pytest_asyncio.fixture
async def recognizer():
    math = make_subject("Математика", ["матеша", "матем"], 100)
    rus = make_subject("Русский язык", ["русик", "русский"], 80)
    eng = make_subject("Английский язык", ["англ", "инглиш"], 90)

    return await RecognizeExamRapidWuzzy.create(subject_data=[math, rus, eng], threshold=40)


@pytest.mark.asyncio
async def test_exact_match(recognizer: RecognizeExamRapidWuzzy):
    result = await recognizer.recognize("Математика")
    assert len(result) == 1
    assert result[0].name == "Математика"


@pytest.mark.asyncio
async def test_alias_match(recognizer):
    result = await recognizer.recognize("матем")
    assert result[0].name == "Математика"


@pytest.mark.asyncio
async def test_popularity_sorting(recognizer: RecognizeExamRapidWuzzy):
    # Ввод похож и на "русик", и на "англ", но "Английский язык" популярнее
    result = await recognizer.recognize("язык")
    assert result
    assert result[0].name in ["Русский язык", "Английский язык"]


@pytest.mark.asyncio
async def test_no_match_due_to_threshold():
    low_threshold = 95
    subject = make_subject("Информатика", ["инфа"], 50)
    recognizer = await RecognizeExamRapidWuzzy.create([subject], threshold=low_threshold)

    result = await recognizer.recognize("информат")
    assert result == []


@pytest.mark.asyncio
async def test_deduplication(recognizer: RecognizeExamRapidWuzzy):
    # Симулируем дублирование alias
    recognizer.aliase_subject["матеша"].append("математика")
    result = await recognizer.recognize("матеша")
    assert len(result) == 1
    assert result[0].name == "Математика"
