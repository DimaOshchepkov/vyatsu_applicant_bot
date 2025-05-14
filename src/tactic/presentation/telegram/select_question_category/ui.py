from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.text import List as TextList

from tactic.presentation.telegram.select_question_category.getters import (
    category_getter,
    question_getter,
)
from tactic.presentation.telegram.select_question_category.handlers import (
    on_back_clicked,
    on_category_selected,
    on_question_selected,
)
from tactic.presentation.telegram.states import CategoryStates

category_select = Column(
    Select(
        Format("{item.title}"),
        id="category_select",
        item_id_getter=lambda c: str(c.id),
        items="categories",
        on_click=on_category_selected,
    )
)


number_buttons = Row(
    Select(
        Format("{item}"),
        id="question_buttons",
        item_id_getter=lambda i: str(i),
        items="button_indices",
        on_click=on_question_selected,
    )
)


question_window = Window(
    Format("Вопросы по категории:\n{path}\n"),
    TextList(
        Format("{item}"),
        items="questions",
    ),
    number_buttons,
    Button(Const("Назад"), id="back", on_click=on_back_clicked),
    state=CategoryStates.questions,
    getter=question_getter,
)


category_window = Window(
    Format("Выберите категорию:\n{path}"),
    category_select,
    Button(Const("Назад"), id="back", on_click=on_back_clicked),
    state=CategoryStates.browsing,
    getter=category_getter,
)
