import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from db.user import update_user
from keyboards.menu import menu_main
from keyboards.profile import menu_edit_request_contact

router = Router()


def validate_phone(phone: str) -> bool:
    pattern = re.compile(
        r"^(?:\+7|8|7)"  # начинается с +7, 7 или 8
        r"[\s\-]?"  # опциональный пробел или дефис
        r"(?:\(?\d{3}\)?[\s\-]?)"  # код региона: 3 цифры, может быть в скобках, с пробелом/дефисом
        r"\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$"  # номер: 3 цифры - 2 цифры - 2 цифры с опциональными пробелами/дефисами
    )
    return bool(pattern.match(phone))


class StateEditProfile(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()


@router.callback_query(F.data == "edit_first_name")
async def edit_first_name(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(StateEditProfile.first_name)
    await bot.send_message(
        callback.from_user.id, "Введите новое имя:", reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()


@router.message(StateEditProfile.first_name)
async def save_first_name(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("\u274c Имя не может быть пустым. Повторите ввод.")
        return

    if len(message.text.strip()) > 10:
        await message.answer(
            "\u274c Имя слишком длинное. Максимум 10 символов. Повторите ввод."
        )
        return

    if message.from_user:
        await update_user(user_id=message.from_user.id, first_name=message.text.strip())
        await state.clear()
        await message.answer("Имя обновлено \u2705", reply_markup=menu_main)


@router.callback_query(F.data == "edit_last_name")
async def edit_last_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StateEditProfile.last_name)
    await callback.message.answer(
        "Введите новую фамилию:", reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()


@router.message(StateEditProfile.last_name)
async def save_last_name(message: Message, state: FSMContext):
    await update_user(user_id=message.from_user.id, last_name=message.text.strip())
    await state.clear()
    await message.answer("Фамилия обновлена \u2705", reply_markup=menu_main)


@router.callback_query(F.data == "edit_username")
async def update_username(callback: CallbackQuery):
    username = callback.from_user.username
    if not username:
        await callback.message.answer(
            "\u274c Не удалось получить username из Telegram."
        )
    else:
        await update_user(user_id=callback.from_user.id, username=username)
        await callback.message.answer("Никнейм обновлён \u2705", reply_markup=menu_main)
    await callback.answer()


@router.callback_query(F.data == "edit_phone")
async def update_phone(update: CallbackQuery | Message, state: FSMContext):
    await state.set_state(StateEditProfile.phone)

    if isinstance(update, CallbackQuery):
        await update.message.answer(
            "Отправьте контакт, нажав кнопку, или введите номер телефона вручную в формате 79123456789:",
            reply_markup=menu_edit_request_contact,
        )
        await update.answer()
    elif isinstance(update, Message):
        await update.answer(
            "Отправьте контакт, нажав кнопку, или введите номер телефона вручную в формате 79123456789:",
            reply_markup=menu_edit_request_contact,
        )


@router.message(StateEditProfile.phone)
async def save_phone(message: Message, state: FSMContext):
    phone = None
    if message.contact and message.contact.phone_number:
        phone = message.contact.phone_number
    elif message.text and validate_phone(message.text.strip()):
        phone = message.text.strip()

    if not phone:
        await message.answer("\u274c Неверный формат номера. Повторите ввод.")
        return

    await update_user(user_id=message.from_user.id, phone=phone)
    await state.clear()
    await message.answer("Телефон обновлён \u2705", reply_markup=menu_main)

