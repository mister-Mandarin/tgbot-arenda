from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Забронировать зал")],
        [KeyboardButton(text="👤 Мой профиль")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)