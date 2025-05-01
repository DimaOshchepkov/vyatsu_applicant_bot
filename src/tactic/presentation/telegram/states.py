from aiogram.fsm.state import StatesGroup, State


class NewUser(StatesGroup):
    user_id = State()


class ExamDialog(StatesGroup):
    input_exam = State()
    choose_exam = State()