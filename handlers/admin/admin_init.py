from services.helpers import ADMIN_IDS
from keyboards.menu import menu_main
from db.user import update_user, get_count_users, get_all_users
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


async def start_admin(user_id: int, message: Message):
    update_user(user_id=user_id, role="admin")
    await message.answer(f"Поздравляю! Ты великий и могучий админ в этом боте! Это собщениевядит только избранные и ты в их числе! Для тебя доступна секретная команда /iadmin для доступа к дополнительным функциям.", reply_markup=menu_main)


async def notify_admins(state: FSMContext, bot: Bot):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    text = await get_state(state, "reservation_text")

    text_message = (
        '''
        📢🆕✨ Новая бронь! ✨🆕📢\n\n
        📅 Время заявки: {now} 📅\n\n
        {text}
        '''
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text_message, parse_mode="HTML")
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.error(f"Не удалось отправить админу {admin_id}: {e}")


@admin_router.message(IsAdmin(), Command(commands=["iadmin"], prefix="/"))
async def open_admin_panel(message: Message):
    await message.answer(f"Панель управления!\nВыбери действие из меню:", reply_markup=menu_admin)


@admin_router.callback_query(F.data == "admin_count_users")
async def check_count_users(callback: CallbackQuery, bot: Bot):
    row = await asyncio.to_thread(get_count_users)
    await bot.send_message(
        callback.from_user.id,
        text=(
            "📊 <b>Статистика бота</b>\n\n"
            f"👤 Всего пользователей: <b>{row[0]}</b>\n"
            f"🛡️ Администраторов: <b>{row[1]}</b>\n"
            f"🚫 Неактивных: <b>{row[2]}</b>"
        )
    )
    await callback.answer()
