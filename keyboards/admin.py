from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

menu_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Cообщение всем пользователям", callback_data="admin_broadcast")],
        [InlineKeyboardButton(
            text="Количество пользователей", callback_data="admin_count_users")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

menu_admin_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="❌ Отмена рассылки", callback_data="broadcast_cancel")]
    ],
    resize_keyboard=True
)

menu_admin_broadcast = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Отправить",
                             callback_data="broadcast_confirm"),
        InlineKeyboardButton(text="✏️ Изменить",
                             callback_data="broadcast_change")
    ],
    [InlineKeyboardButton(text="❌ Отмена рассылки", callback_data="broadcast_cancel")]
])
