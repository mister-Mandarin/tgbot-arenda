from aiogram import Router, types
from db.user import get_user, create_user
from aiogram.filters import CommandStart
from keyboards.menu import menu_main

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    tg_user = message.from_user
    db_user = get_user(tg_user.id)

    if not db_user:
        create_user(
            user_id=tg_user.id,
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name,
            username=tg_user.username
            # phone=tg_user.phone_number or ""
        )
        text = f"👋 Привет {tg_user.first_name}! Ты зарегистрирован в системе."
        await message.answer(text, reply_markup=menu_main)
    else:
        text = f"👋 С возвращением, {db_user[1]}!"
        await message.answer(text, reply_markup=menu_main)

