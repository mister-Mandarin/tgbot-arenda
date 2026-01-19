from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

menu_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Cообщение всем пользователям", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="Количество пользователей",
                              callback_data="admin_count_users")],
        # [InlineKeyboardButton(text="Возврат в главное меню пользователя", callback_data="admin_return_main")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)
