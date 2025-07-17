from services.helpers import ADMIN_IDS
from keyboards.menu import menu_main
from db.user import update_user
from aiogram.types import Message
from services.helpers import ADMIN_IDS
from datetime import datetime
from aiogram.fsm.context import FSMContext
from services.helpers import get_state
from db.user import get_user_admins

ADMIN_DB = []

def admin_db_cached():
    global ADMIN_DB
    if not ADMIN_DB:
        ADMIN_DB = get_user_admins()
    return ADMIN_DB

async def start_admin(user_id, message: Message):
        if user_id in ADMIN_IDS:
            update_user(user_id=user_id, role="admin")
            await message.answer(f"Поздравляю! Ты великий и могучий админ в этом боте! Это собщениевядит только избранные и ты в их числе!", reply_markup=menu_main)

async def notify_admins(message: Message, state: FSMContext):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    text = await get_state(state, "reservation_text")
    text_message = (
        f"📢🆕✨ Новая бронь! ✨🆕📢\n\n"
        f"📅 Время заявки: {now} 📅\n\n"
        + text
    )

    admins = admin_db_cached()

    for admin_id in admins:
        await message.bot.send_message(admin_id, text_message, parse_mode="HTML")
