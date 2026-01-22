import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import AiogramError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from db.user import get_all_users
from handlers.callback_factory import BroadcastState
from keyboards.admin import menu_admin_broadcast, menu_admin_cancel
from keyboards.menu import menu_main
from services.admin_filter import IsAdmin

admin_router = Router()
admin_router.callback_query.filter(IsAdmin())
admin_router.message.filter(IsAdmin())


@admin_router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(BroadcastState.waiting_for_input)
    await bot.send_message(
        callback.from_user.id, text="____", reply_markup=ReplyKeyboardRemove()
    )

    await callback.answer()

    await bot.send_message(
        callback.from_user.id,
        text="✍️ <b>Напиши текст для рассылки.</b>",
        reply_markup=menu_admin_cancel,
    )
    await callback.answer()


@admin_router.callback_query(
    StateFilter(BroadcastState.waiting_for_input, BroadcastState.waiting_for_confirm),
    F.data == "broadcast_cancel",
)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.send_message(
        callback.from_user.id, text="❌ Рассылка отменена.", reply_markup=menu_main
    )
    await callback.answer()


@admin_router.message(BroadcastState.waiting_for_input)
async def process_broadcast(message: Message, state: FSMContext):
    # Записываю данные сообщения для предпросмотра
    await state.update_data(msg_id=message.message_id, chat_id=message.chat.id)

    await state.set_state(BroadcastState.waiting_for_confirm)

    await message.reply(
        "<b>👁️ Предпросмотр рассылки</b>\n\n"
        "Выше — ваше сообщение в том виде, в котором его получат юзеры. Отправляем?",
        reply_markup=menu_admin_broadcast,
    )


@admin_router.callback_query(
    BroadcastState.waiting_for_confirm, F.data == "broadcast_change"
)
async def change_message(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(BroadcastState.waiting_for_input)
    await state.update_data(msg_id=None, chat_id=None)
    if callback.message:
        await bot.delete_message(
            chat_id=callback.from_user.id, message_id=callback.message.message_id
        )
        await bot.send_message(
            callback.from_user.id,
            text="✍️ Хорошо, пришлите новое сообщение (предыдущее забыли).",
        )
    await callback.answer()


async def send_message_safe(bot: Bot, user_id: int, msg_id: int, chat_id: int) -> bool:
    """Отправка сообщения с обработкой типичных ошибок"""
    try:
        await bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=msg_id)
        return True
    except AiogramError as e:
        logging.error("Ну удалось отправить сообщение %s", {e})
        await bot.send_message(chat_id=271737651, text=f"[ERROR]: {user_id} {e}")
        await asyncio.sleep(0.3)

    return False


async def go_broadcast(
    bot: Bot, users_ids: list[int], msg_id: int, chat_id: int
) -> int:
    """Основной цикл рассылки"""
    count = 0
    for user_id in users_ids:
        success = await send_message_safe(bot, user_id, msg_id, chat_id)
        if success:
            count += 1
        await asyncio.sleep(0.1)
    return count


@admin_router.callback_query(
    BroadcastState.waiting_for_confirm, F.data == "broadcast_confirm"
)
async def confirm_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id", 0)
    chat_id = data.get("chat_id", 0)

    if callback.message:
        await bot.delete_message(
            chat_id=callback.from_user.id, message_id=callback.message.message_id
        )
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="⏳ <b>Рассылка запущена...</b>",
            reply_markup=None,
        )
        await callback.answer()

    users_ids = await asyncio.to_thread(get_all_users)

    count = await go_broadcast(bot, users_ids, msg_id, chat_id)

    await bot.send_message(
        chat_id=callback.from_user.id,
        text=f"✅ <b>Рассылка завершена!</b>\nПолучили: {count} чел.",
        reply_markup=menu_main,
    )
    await state.clear()
    await callback.answer()
