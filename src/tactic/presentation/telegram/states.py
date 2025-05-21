from aiogram.fsm.state import StatesGroup, State


class NewUser(StatesGroup):
    user_id = State()


class ExamDialog(StatesGroup):
    input_exam = State()
    choose_match = State()
    choose_final = State()
    input_interests = State()
    show_programs = State()
    
    
class CategoryStates(StatesGroup):
    browsing = State()
    questions = State()
    search_results = State()
    