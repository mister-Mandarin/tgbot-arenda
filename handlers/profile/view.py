from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from db.user import get_user
from keyboards.profile import menu_edit_profile, menu_edit_profile_fields

router = Router()


@router.message(F.text == "👤 Мой профиль")
async def show_profile(message: Message):
    user = get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Пользователь не найден.")
        return

    profile_text = (
        f"<b>Ваш профиль</b>\n"
        f"🧑 Имя: {user['first_name']}\n"
        f"👥 Фамилия: {user['last_name'] or '-'}\n"
        f"📱 Телефон: {user['phone'] or '-'}\n"
        f"📛 Никнейм: @{user['username'] if user['username'] else '-'}\n"
    )

    await message.answer(profile_text, reply_markup=menu_edit_profile)


async def show_profile_edit_menu(chat_id, bot):
    await bot.send_message(
        chat_id,
        "Выберите параметры профиля которые хотите изменить: 👇",
        reply_markup=menu_edit_profile_fields,
    )


@router.callback_query(F.data == "edit_profile")
async def on_edit_profile_callback(callback: CallbackQuery):
    await callback.answer()
    await show_profile_edit_menu(callback.from_user.id, callback.bot)


@router.message(F.text == "📋 Редактировать профиль")
async def on_edit_profile_message(message: Message):
    await show_profile_edit_menu(message.chat.id, message.bot)
