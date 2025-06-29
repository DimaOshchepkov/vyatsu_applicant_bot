from aiogram.types import ContentType
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Column,
    Group,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
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
    reopen_search_results,
)
from tactic.presentation.telegram.states import CategoryStates


def category_select():

    def is_long_list(data: dict, widget: Whenable, dialog_manager: DialogManager):
        return len(data.get("categories", [])) > 9

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


number_buttons = Group(
    Select(
        Format("{item}"),
        id="question_buttons",
        item_id_getter=lambda i: str(i),
        items="button_indices",
        on_click=on_question_selected,
    ),
    width=8,
)

def back_button():
    return Button(Const("Назад"), id="back", on_click=on_back_clicked)
question_window = Window(
    Format("Вопросы по категории:\n{path}\n"),
    TextList(
        Format("{item}"),
        items="questions",
    ),
    number_buttons,
    Row(back_button(), to_menu()),
    state=CategoryStates.questions,
    getter=question_getter,
)


category_window = Window(
    Format("Выберите категорию или введите вопрос с клавиатуры\n{path}"),
    *category_select(),
    back_button(),
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
    MessageInput(reopen_search_results),
    number_vector_db_buttons,
    Row(
        back_button(),
        to_menu(),
    ),
    state=CategoryStates.search_results,
    getter=question_from_vector_db_getter,
)
