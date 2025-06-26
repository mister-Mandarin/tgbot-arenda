from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from services.helpers import LIST_HALLS

# menu_hall_check = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="120/Классика", callback_data="check_big120"),
#         InlineKeyboardButton(text="90/Эзотерика", callback_data="check_big90")],
#         [InlineKeyboardButton(text="60/Романтика", callback_data="check_medium60"),
#         InlineKeyboardButton(text="30/Практика", callback_data="check_small30")],
#         [InlineKeyboardButton(text="Кабинет 16/Массаж", callback_data="check_small16")]
#     ]
# )

buttons = []

for hall in LIST_HALLS:
    button = InlineKeyboardButton(
        text=hall["name"],
        callback_data=f"check_{hall['alias']}"
    )
    buttons.append(button)

keyboard = []
for i in range(0, len(buttons), 2):
    row = buttons[i:i + 2]  # Берём 2 кнопки за раз
    keyboard.append(row)

menu_hall_check = InlineKeyboardMarkup(inline_keyboard=keyboard)