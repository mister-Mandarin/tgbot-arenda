from aiogram.filters.callback_data import CallbackData

# Колбек-фабрика времени
class SelectTimeStartCallback(CallbackData, prefix="select_time_start"):
    value: str

class SelectTimeEndCallback(CallbackData, prefix="select_time_end"):
    value: str