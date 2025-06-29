from aiogram.fsm.state import State, StatesGroup


class NewUser(StatesGroup):
    user_id = State()


class ExamDialog(StatesGroup):
    choose_education_level = State()
    choose_contest_type = State()
    input_exam = State()
    choose_match = State()
    choose_study_form = State()
    input_interests = State()
    show_programs = State()


class CategoryStates(StatesGroup):
    browsing = State()
    questions = State()
    search_results = State()


class ProgramStates(StatesGroup):
    start = State()
    input_program = State()
    select_direction = State()
    choose_payment = State()
    confirm_subscribe = State()
    view_subscriptions = State()
    subscription_settings = State()
