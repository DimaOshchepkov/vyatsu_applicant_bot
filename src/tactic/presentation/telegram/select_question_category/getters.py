import logging

from aiogram_dialog import DialogManager

from tactic.domain.entities.category import CategoryDomain
from tactic.presentation.interactor_factory import InteractorFactory
from tactic.presentation.telegram.select_question_category.context import (
    CategoryViewContext,
    DialogData,
    QuestionFromVectorDbViewContext,
    QuestionViewContext,
)
from tactic.presentation.telegram.select_question_category.dto import ResponseEntry
from tactic.presentation.telegram.select_question_category.utils import format_path

logging.basicConfig(
    level=logging.DEBUG,  # можно поменять на DEBUG при отладке
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def category_getter(dialog_manager: DialogManager, **kwargs):
    data = DialogData.from_manager(dialog_manager)
    
    ioc: InteractorFactory = dialog_manager.middleware_data['ioc']
    async with ioc.get_categories() as get_categories:
        all_categories = await get_categories()
    
    logger.debug(f"Категории в геттере: {all_categories}")

    categories = [cat for cat in all_categories if cat.parent_id == data.parent_id]
    return CategoryViewContext(
        categories=categories, path=format_path(data.path)
    ).to_dict()


async def question_getter(dialog_manager: DialogManager, **kwargs):
    data = DialogData.from_manager(dialog_manager)

    ioc: InteractorFactory = dialog_manager.middleware_data["ioc"]
    async with ioc.get_questions_by_category_id() as questions:
        questions_by_category = await questions(data.parent_id or -1)

    data.last_questions = [q.model_dump() for q in questions_by_category]
    data.update_manager(dialog_manager)

    numbered_questions = [
        f"{i+1}. {q.question}" for i, q in enumerate(questions_by_category)
    ]

    return QuestionViewContext(
        questions=numbered_questions,
        path=format_path(data.path),
        button_indices=list(range(1, len(numbered_questions) + 1)),
    ).to_dict()


async def question_from_vector_db_getter(dialog_manager: DialogManager, **kwargs):
    data = DialogData.from_manager(dialog_manager)

    search_results = [
        ResponseEntry.model_validate(entry) for entry in data.search_results
    ]

    numbered_questions = [f"{i+1}. {q.question}" for i, q in enumerate(search_results)]

    return QuestionFromVectorDbViewContext(
        questions=numbered_questions,
        path=format_path(data.path),
        button_indices=list(range(1, len(numbered_questions) + 1)),
        search_query=data.search_query,
    ).to_dict()
