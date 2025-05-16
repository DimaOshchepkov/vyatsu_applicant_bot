from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, Row, Select
from aiogram_dialog.widgets.text import Format

from tactic.presentation.telegram.select_exam.getters import matched_exams_getter
from tactic.presentation.telegram.select_exam.handlers import (
    exam_input_handler,
    on_cancel_handler,
    on_exam_chosen_handler,
    on_finish_handler,
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
