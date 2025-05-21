from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Column, ListGroup, Row, Select, Url
from aiogram_dialog.widgets.link_preview import LinkPreview
from aiogram_dialog.widgets.text import Const, Format

from tactic.presentation.telegram.select_exam.getters import (
    matched_exams_getter,
    programs_getter,
)
from tactic.presentation.telegram.select_exam.handlers import (
    exam_input_handler,
    on_cancel_handler,
    on_exam_chosen_handler,
    on_finish_handler,
    on_interest_entered_handler,
)
from tactic.presentation.telegram.states import ExamDialog

input_exam_window = Window(
    Format("Введите название экзамена:"),
    TextInput(id="exam_input", on_success=exam_input_handler),
    Row(
        Button(text=Format("✅ Закончить"), id="finish", on_click=on_finish_handler),
        Button(text=Format("❌ Отменить"), id="cancel", on_click=on_cancel_handler),
    ),
    state=ExamDialog.input_exam,
)


choose_match_window = Window(
    Format("Выберите наиболее подходящий экзамен:"),
    Column(
        Select(
            text=Format("{item[title]}"),
            id="match_select",
            item_id_getter=lambda item: item["id"],
            items="matches",
            on_click=on_exam_chosen_handler,
        )
    ),
    getter=matched_exams_getter,
    state=ExamDialog.choose_match,
)


input_interests_window = Window(
    Format("Введите ваши интересы (в свободной форме):"),
    TextInput(id="interest_input", on_success=on_interest_entered_handler),
    state=ExamDialog.input_interests,
)


show_programs_window = Window(
    Const("Вот подходящие направления:"),
    ListGroup(
        Url(
            Format("{item[title]} — {item[score]:.2f}"),
            Format("{item[url]}"),
            id="program_url",
        ),
        id="program_list",
        item_id_getter=lambda item: item["program_id"],
        items="programs",
    ),
    getter=programs_getter,
    state=ExamDialog.show_programs,
)
