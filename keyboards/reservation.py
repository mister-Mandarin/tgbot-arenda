from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from services.helpers import LIST_HALLS
from handlers.callback_factory import SelectTimeStartCallback, SelectTimeEndCallback

def build_menu_hall_check():
    keyboard = []    
    buttons = []
# Формируем список залов
    for hall in LIST_HALLS:
        button = InlineKeyboardButton(
            text=hall["name"],
            callback_data=f"check_{hall['alias']}"
        )
        buttons.append(button)
# Позиционирование кнопок
    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]  # Берём 2 кнопки за раз
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

menu_hall_check = build_menu_hall_check()

def build_time_row_start(slots: list[str]) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text=slot,
            callback_data=SelectTimeStartCallback(value=slot.replace(":", "-")).pack()
        )
        for slot in slots
    ]


def build_time_row_end(slots: list[str]) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text=slot,
            callback_data=SelectTimeEndCallback(value=slot.replace(":", "-")).pack()
        )
        for slot in slots
    ]

def menu_hall_time(slots: list[str], is_end: bool = False) -> InlineKeyboardMarkup:
    rows = []
    build_row = None
    if is_end:
        build_row = build_time_row_end
    else:
        build_row = build_time_row_start
    for i in range(0, len(slots), 4):
        chunk = slots[i:i + 4]
        row = build_row(chunk)

        while len(row) < 4:
            row.append(InlineKeyboardButton(text=" ", callback_data="empty"))
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


menu_hall_change_date = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Выбрать другую дату")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Вы можете изменить дату бронирования"
)

menu_hall_confirm = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Подтвердить бронирование")],
        [
            KeyboardButton(text="✏️ Изменить бронь"),
            KeyboardButton(text="📋 Редактировать профиль")
        ],
        [
            KeyboardButton(text="❌ Отмена"),
            #KeyboardButton(text="❓ Помощь")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Подтвердите данные бронирования"
)