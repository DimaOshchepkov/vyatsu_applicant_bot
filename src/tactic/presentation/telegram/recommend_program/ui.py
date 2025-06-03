from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Column, ListGroup, Row, Select, Url
from aiogram_dialog.widgets.text import Const, Format

from tactic.presentation.telegram.recommend_program.getters import (
    contest_types_getter,
    education_levels_getter,
    matched_exams_getter,
    programs_getter,
    study_forms_getter,
)
from tactic.presentation.telegram.recommend_program.handlers import (
    exam_input_handler,
    on_back,
    on_cancel_handler,
    on_contest_type_chosen,
    on_education_level_chosen,
    on_exam_chosen_from_keyboard_handler,
    on_exam_chosen_handler,
    on_finish_handler,
    on_interest_entered_handler,
    on_skip,
    on_study_form_chosen,
)
from tactic.presentation.telegram.states import ExamDialog


def progress_bar(current: int, total: int) -> Const:
    return Const(f"Шаг {current} из {total}")


def nav_buttons():
    return [
        Button(Const("⏮ Назад"), id="back", on_click=on_back),
        Button(Const("⏭ Пропустить"), id="skip", on_click=on_skip),
    ]


education_level_window = Window(
    progress_bar(1, 5),
    Const("Выберите уровень образования:"),
    Column(
        Select(
            Format("{item[name]}"),
            id="education_level",
            item_id_getter=lambda x: x["id"],
            items="education_levels",  # getter должен передать список
            on_click=on_education_level_chosen,
        )
    ),
    Row(*nav_buttons()),
    getter=education_levels_getter,
    state=ExamDialog.choose_education_level,
)

contest_type_window = Window(
    progress_bar(3, 5),
    Const("Выберите тип вступительных испытаний:"),
    Column(
        Select(
            Format("{item[name]}"),
            id="contest_type",
            item_id_getter=lambda item: item["id"],
            items="contest_types",
            on_click=on_contest_type_chosen,
        )
    ),
    Row(*nav_buttons()),
    getter=contest_types_getter,
    state=ExamDialog.choose_exam_type,
)


input_exam_window = Window(
    progress_bar(4, 5),
    Const("Введите название экзамена:"),
    TextInput(id="exam_input", on_success=exam_input_handler),
    Row(
        Button(Const("⏮ Назад"), id="back", on_click=on_back),
        Button(Const("✅ Закончить"), id="finish", on_click=on_finish_handler),
        Button(Const("⏭ Пропустить"), id="skip", on_click=on_skip),
    ),
    state=ExamDialog.input_exam,
)


choose_match_window = Window(
    progress_bar(4, 5),
    Const("Выберите наиболее подходящий экзамен:"),
    Column(
        Select(
            text=Format("{item[title]}"),
            id="match_select",
            item_id_getter=lambda item: item["id"],
            items="matches",
            on_click=on_exam_chosen_handler,
        )
    ),
    TextInput[int](
        id="manual_input",
        on_success=on_exam_chosen_from_keyboard_handler,
        type_factory=int,
    ),
    Row(*nav_buttons()),
    getter=matched_exams_getter,
    state=ExamDialog.choose_match,
)


study_form_window = Window(
    progress_bar(2, 5),
    Const("Выберите форму обучения:"),
    Column(
        Select(
            Format("{item[name]}"),
            id="study_form",
            item_id_getter=lambda x: x["id"],
            items="study_forms",  # например: ["Очная", "Заочная", "Очно-заочная"]
            on_click=on_study_form_chosen,
        )
    ),
    Row(*nav_buttons()),
    getter=study_forms_getter,
    state=ExamDialog.choose_study_form,
)


input_interests_window = Window(
    progress_bar(5, 5),
    Const("Введите ваши интересы (в свободной форме):"),
    TextInput(id="interest_input", on_success=on_interest_entered_handler),
    Row(*nav_buttons()),
    state=ExamDialog.input_interests,
)


show_programs_window = Window(
    Const("Список отранжированных направлений:"),
    ListGroup(
        Url(
            Format("{item[title]}"),
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
