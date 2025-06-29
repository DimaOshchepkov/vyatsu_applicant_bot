import logging
from collections import OrderedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import TimelineType
from tactic.domain.entities.timeline_type import PaymentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()  # корневой логгер

TIMELINE_TYPE_NAMES = OrderedDict(
    {
        PaymentType.PAID: "paid_endpoints",
        PaymentType.BUDGET: "budget_endpoints",
    }
)


async def check_timeline_types(session: AsyncSession) -> bool:
    try:
        result = await session.execute(select(TimelineType))
        rows = result.scalars().all()
    except Exception as e:
        logger.error("⚠️ Ошибка при запросе к таблице timeline_type: %s", e)
        return True

    db_timeline_types = {row.id: row.name for row in rows}

    errors = False

    for enum_key, expected_name in TIMELINE_TYPE_NAMES.items():
        db_name = db_timeline_types.get(enum_key.value)
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

    expected_ids = {tt.value for tt in TIMELINE_TYPE_NAMES}
    actual_ids = set(db_timeline_types)
    extra_ids = actual_ids - expected_ids

    for db_id in extra_ids:
        logger.warning(
            "⚠️ В базе есть лишняя запись: id=%d, name='%s'",
            db_id,
            db_timeline_types[db_id],
        )
        errors = True

    if not errors:
        logger.info("✅ Все типы в timeline_type корректны.")

    return errors
