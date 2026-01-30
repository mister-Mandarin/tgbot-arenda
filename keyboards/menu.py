from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Забронировать зал")],
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="ℹ️ Условия бронирования")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
