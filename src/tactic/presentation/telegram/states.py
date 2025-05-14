from aiogram.fsm.state import StatesGroup, State


class NewUser(StatesGroup):
    user_id = State()


class ExamDialog(StatesGroup):
    input_exam = State()         # Ввод текста
    choose_match = State()       # Выбор из ближайших экзаменов
    choose_final = State()       # Финальный список
    
    
class CategoryStates(StatesGroup):
    browsing = State()
    questions = State()