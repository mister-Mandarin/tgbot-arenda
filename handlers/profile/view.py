from aiogram import Router, F
from db.user import get_user
from aiogram.types import CallbackQuery, Message
from keyboards.menu import menu_edit_profile, menu_edit_profile_fields

router = Router()

@router.message(F.text == "📋 Мой профиль")
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

    await message.answer(profile_text, parse_mode="HTML", reply_markup=menu_edit_profile)

@router.callback_query(F.data == 'edit_profile')
async def show_requests(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer("Выберите параметры профиля которые хотите изменить: 👇", reply_markup=menu_edit_profile_fields)

# @router.message(F.text == "Мой профиль")
# async def show_profile(message: Message):
#     await message.answer("Ответ")

# @router.callback_query(F.data == 'profile')
# async def show_requests(callback: CallbackQuery):
#     await callback.answer('')
#     await callback.message.edit_text("profile")
