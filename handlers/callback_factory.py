from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup


class SelectTimeStartCallback(CallbackData, prefix="select_time_start"):
    value: str


class SelectTimeEndCallback(CallbackData, prefix="select_time_end"):
    value: str


class BroadcastState(StatesGroup):
    waiting_for_input = State()       # Ждем текст/фото
    waiting_for_confirm = State()     # Ждем нажатия кнопки
