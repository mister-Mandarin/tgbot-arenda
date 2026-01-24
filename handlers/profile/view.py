from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from db.user import get_user, update_user_notifications
from keyboards.profile import (
    menu_edit_profile_active,
    menu_edit_profile_fields,
    menu_edit_profile_inactive,
)

router = Router()


@router.message(F.text == "👤 Мой профиль")
async def show_profile(message: Message):
    if not message.from_user:
        return

    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Пользователь не найден.")
        return

    profile_text = (
        f"<b>Ваш профиль</b>\n"
        f"🧑 Имя: {user['first_name']}\n"
        f"👥 Фамилия: {user['last_name'] or '-'}\n"
        f"📱 Телефон: {user['phone'] or '-'}\n"
        f"📛 Никнейм: @{user['username'] if user['username'] else '-'}\n"
        f"🔔 Рассылка: {'Активна' if user['notifications'] else 'Неактивна'}\n"
    )

    await message.answer(
        profile_text,
        reply_markup=menu_edit_profile_active
        if user["notifications"]
        else menu_edit_profile_inactive,
    )


async def show_profile_edit_menu(chat_id: int, bot: Bot):
    await bot.send_message(
        chat_id,
        "Выберите параметры профиля которые хотите изменить: 👇",
        reply_markup=menu_edit_profile_fields,
    )


@router.callback_query(F.data == "edit_profile")
async def on_edit_profile_callback(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await show_profile_edit_menu(callback.from_user.id, bot)


@router.message(F.text == "📋 Редактировать профиль")
async def on_edit_profile_message(message: Message, bot: Bot):
    await show_profile_edit_menu(message.chat.id, bot)


@router.callback_query(F.data == "edit_notifications")
async def on_edit_notifications_callback(callback: CallbackQuery, bot: Bot):
    new_status = await update_user_notifications(callback.from_user.id)

    status_text = "🔔 Включены" if new_status else "🔕 Выключены"

    await bot.send_message(
        callback.from_user.id,
        f"Статус уведомлений изменен на: <b>{status_text}</b>",
    )
    await callback.answer()
