import asyncio
import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from db.user import get_statistics_users, update_user
from keyboards.admin import menu_admin
from keyboards.menu import menu_main
from services.admin_filter import IsAdmin
from services.helpers import ADMIN_IDS

admin_router = Router()
admin_router.callback_query.filter(IsAdmin())
admin_router.message.filter(IsAdmin())


async def start_admin(user_id: int, message: Message):
    await update_user(user_id=user_id, role="admin")
    await message.answer(
        "Ты великий и могучий админ в этом боте! Для тебя доступна секретная команда /iadmin",
        reply_markup=menu_main,
    )


async def notify_admins(text: str, bot: Bot):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    text_message = f"📢🆕✨ Новая заяка! ✨🆕📢\n\n📅 Время: {now} 📅\n\n{text}"

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text_message)
            await asyncio.sleep(0.05)
        except TelegramAPIError as e:
            logging.error("Не удалось отправить админу %s: %s", admin_id, e)


@admin_router.message(IsAdmin(), Command(commands=["iadmin"], prefix="/"))
async def open_admin_panel(message: Message):
    await message.answer(
        "Панель управления!\nВыбери действие из меню:", reply_markup=menu_admin
    )


@admin_router.callback_query(F.data == "admin_statistics_users")
async def check_count_users(callback: CallbackQuery, bot: Bot):
    total, notified, inactive, admins = await get_statistics_users()
    await bot.send_message(
        callback.from_user.id,
        text=(
            "📊 <b>Статистика бота</b>\n\n"
            f"👤 Всего пользователей: <b>{total}</b>\n"
            f"📝 Получают рассылку: <b>{notified}</b>\n"
            f"🚫 Заблокировали бота: <b>{inactive}</b>\n"
            f"🛡️ Администраторы: <b>{admins}</b>\n"
        ),
    )
    await callback.answer()
