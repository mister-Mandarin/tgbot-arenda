from services.helpers import ADMIN_IDS
from keyboards.menu import menu_main
from db.user import update_user, count_users
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from aiogram.fsm.context import FSMContext
from services.helpers import get_state
import logging
import asyncio
from aiogram import Router, F, Bot
from services.admin_filter import IsAdmin
from aiogram.filters import Command
from keyboards.admin import menu_admin

admin_router = Router()
admin_router.callback_query.filter(IsAdmin())
admin_router.message.filter(IsAdmin())


async def start_admin(user_id, message: Message):
    if user_id in ADMIN_IDS:
        update_user(user_id=user_id, role="admin")
        await message.answer(f"Поздравляю! Ты великий и могучий админ в этом боте! Это собщениевядит только избранные и ты в их числе! Для тебя доступна секретная команда /iadmin для доступа к дополнительным функциям.", reply_markup=menu_main)


async def notify_admins(message: Message, state: FSMContext, bot: Bot):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    text = await get_state(state, "reservation_text")
    text_message = (
        f"📢🆕✨ Новая бронь! ✨🆕📢\n\n"
        f"📅 Время заявки: {now} 📅\n\n"
        f"{text}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text_message, parse_mode="HTML")
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.error(f"Не удалось отправить админу {admin_id}: {e}")


@admin_router.message(IsAdmin(), Command(commands=["iadmin"], prefix="/"))
async def open_admin_panel(message: Message):
    await message.answer(f"Добро пожаловать в панель управления!\nВыберите действие из меню ниже:", reply_markup=menu_admin)


@admin_router.callback_query(F.data == "admin_count_users")
async def broadcast_message_prompt(callback: CallbackQuery, bot: Bot):
    user_count = await asyncio.to_thread(count_users)
    await bot.send_message(callback.from_user.id, text=f"Общее количество пользователей бота: {user_count}")
    await callback.answer()
