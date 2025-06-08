from aiogram.types import ContentType
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.text import List as TextList

from tactic.presentation.telegram.new_user.utils import to_menu
from tactic.presentation.telegram.select_question_category.getters import (
    category_getter,
    question_from_vector_db_getter,
    question_getter,
)
from tactic.presentation.telegram.select_question_category.handlers import (
    on_back_clicked,
    on_category_selected,
    on_question_from_vector_db_selected,
    on_question_input,
    on_question_selected,
)
from tactic.presentation.telegram.states import CategoryStates


def category_select():

    def is_long_list(data: dict, widget: Whenable, dialog_manager: DialogManager):
        return len(data.get("categories", [])) > 8

    def make_category_select():
        return Select(
            text=Format("{item[title]}"),
            id="category_select",
            item_id_getter=lambda c: str(c["id"]),
            items="categories",
            on_click=on_category_selected,
        )

    select_widget = make_category_select()

    return (
        ScrollingGroup(
            Column(select_widget),
            id="category_select_scroll",
            width=1,
            height=8,
            when=is_long_list,
            hide_on_single_page=True,
        ),
        Column(
            select_widget,
            when=lambda data, widget, dialog_manager: not is_long_list(
                data, widget, dialog_manager
            ),
        ),
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
    Row(Button(Const("Назад"), id="back", on_click=on_back_clicked), to_menu()),
    MessageInput(on_question_input, content_types=ContentType.TEXT),
    state=CategoryStates.questions,
    getter=question_getter,
)


category_window = Window(
    Format("Выберите категорию или введите вопрос с клавиатуры\n{path}"),
    *category_select(),
    Button(Const("Назад"), id="back", on_click=on_back_clicked),
    MessageInput(on_question_input, content_types=ContentType.TEXT),
    state=CategoryStates.browsing,
    getter=category_getter,
)


number_vector_db_buttons = Row(
    Select(
        Format("{item}"),
        id="question_buttons",
        item_id_getter=lambda i: str(i),
        items="button_indices",
        on_click=on_question_from_vector_db_selected,
    )
)


search_results_window = Window(
    Format('Результаты поиска по запросу:\n"{search_query}"'),
    TextList(
        Format("{item}"),
        items="questions",
    ),
    number_vector_db_buttons,
    Row(Button(Const("Назад"), id="back", on_click=on_back_clicked), to_menu()),
    state=CategoryStates.search_results,
    getter=question_from_vector_db_getter,
)
