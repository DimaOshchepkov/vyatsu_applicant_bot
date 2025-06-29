import logging
from collections import OrderedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import EducationLevel
from tactic.domain.entities.education_level import EducationLevelEnum

logger = logging.getLogger(__name__)

# Ожидаемые значения в БД
EDUCATION_LEVEL_NAMES = OrderedDict(
    {
        EducationLevelEnum.MASTER: "Магистратура",
        EducationLevelEnum.BACHELOR: "Бакалавриат/Специалитет",
        EducationLevelEnum.COLLEGE: "Колледж",
        EducationLevelEnum.PHD: "Аспирантура",
    }
)


async def check_education_levels(session: AsyncSession) -> bool:
    try:
        result = await session.execute(select(EducationLevel))
        rows = result.scalars().all()
    except Exception as e:
        logger.error("⚠️ Ошибка при запросе к таблице education_level: %s", e)
        return True

    db_education_levels = {row.id: row.name for row in rows}

    errors = False

    for enum_key, expected_name in EDUCATION_LEVEL_NAMES.items():
        db_name = db_education_levels.get(enum_key.value)
        if db_name is None:
            logger.error(
                "❌ Отсутствует запись id=%d (ожидалось: '%s')",
                enum_key.value,
                expected_name,
            )
            errors = True
        elif db_name != expected_name:
            logger.error(
                "❌ Несоответствие имени для id=%d: в базе '%s', в коде '%s'",
                enum_key.value,
                db_name,
                expected_name,
            )
            errors = True

    expected_ids = {e.value for e in EDUCATION_LEVEL_NAMES}
    actual_ids = set(db_education_levels)
    extra_ids = actual_ids - expected_ids

    for db_id in extra_ids:
        logger.warning(
            "⚠️ В базе есть лишняя запись: id=%d, name='%s'",
            db_id,
            db_education_levels[db_id],
        )
        errors = True

    if not errors:
        logger.info("✅ Все типы в education_level корректны.")

    return errors
