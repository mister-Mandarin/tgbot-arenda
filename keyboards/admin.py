from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Cообщение всем пользователям", callback_data="admin_broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                text="Статистика пользователей", callback_data="admin_statistics_users"
            )
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

menu_admin_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Отмена рассылки", callback_data="broadcast_cancel"
            )
        ]
    ],
    resize_keyboard=True,
)

menu_admin_broadcast = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Отправить", callback_data="broadcast_confirm"
            ),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="broadcast_change"),
        ],
        [
            InlineKeyboardButton(
                text="❌ Отмена рассылки", callback_data="broadcast_cancel"
            )
        ],
    ]
)
