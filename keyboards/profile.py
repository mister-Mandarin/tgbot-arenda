from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

menu_edit_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📋 Редактировать профиль", callback_data="edit_profile")],
    ]
)

menu_edit_profile_fields = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🧑 Имя", callback_data="edit_first_name"),
        InlineKeyboardButton(text="👥 Фамилию", callback_data="edit_last_name")],
        [InlineKeyboardButton(text="📱 Номер телефона", callback_data="edit_phone"),
        InlineKeyboardButton(text="📛 Никнейм", callback_data="edit_username")],
        # [InlineKeyboardButton(text="📋 Редактировать все данные", callback_data="edit_all")]
    ]
)

menu_edit_request_contact = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)