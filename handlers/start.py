from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.user import create_user, get_user
from handlers.admin.admin_init import start_admin
from handlers.profile.edit import update_phone
from keyboards.menu import menu_main
from services.helpers import ADMIN_IDS

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tg_user = message.from_user

    if not tg_user:
        return

    db_user = await get_user(tg_user.id)

    if not db_user:
        await create_user(
            user_id=tg_user.id,
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name,
            username=tg_user.username,
        )

        await message.answer(
            f"👋 Привет {tg_user.first_name}! Ты зарегистрирован в системе.\n\n"
            f"📱 Чтобы мы могли связаться с вами, пожалуйста укажите номер телефона 👇"
        )
        await update_phone(message, state)
    else:
        await message.answer(
            f"👋 С возвращением, {db_user['first_name']}!", reply_markup=menu_main
        )

    if tg_user.id in ADMIN_IDS:
        await start_admin(tg_user.id, message)
