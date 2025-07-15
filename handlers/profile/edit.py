from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from db.user import update_user
from aiogram.fsm.state import StatesGroup, State
from keyboards.menu import menu_main
from keyboards.profile import menu_edit_request_contact
import re

router = Router()

def validate_phone(phone: str) -> bool:
    pattern = re.compile(
        r'^(?:\+7|8|7)'               # начинается с +7, 7 или 8
        r'[\s\-]?'                  # опциональный пробел или дефис
        r'(?:\(?\d{3}\)?[\s\-]?)'  # код региона: 3 цифры, может быть в скобках, с пробелом/дефисом
        r'\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'  # номер: 3 цифры - 2 цифры - 2 цифры с опциональными пробелами/дефисами
    )
    return bool(pattern.match(phone))

class StateEditProfile(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()

@router.callback_query(F.data == "edit_first_name")
async def edit_first_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StateEditProfile.first_name)
    await callback.message.answer("Введите новое имя:", reply_markup=ReplyKeyboardRemove())
    await callback.answer()

@router.message(StateEditProfile.first_name)
async def save_first_name(message: Message, state: FSMContext):
    update_user(user_id=message.from_user.id, first_name=message.text.strip())
    await state.clear()
    await message.answer("Имя обновлено \u2705", reply_markup=menu_main)

@router.callback_query(F.data == "edit_last_name")
async def edit_last_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StateEditProfile.last_name)
    await callback.message.answer("Введите новую фамилию:", reply_markup=ReplyKeyboardRemove())
    await callback.answer()

@router.message(StateEditProfile.last_name)
async def save_last_name(message: Message, state: FSMContext):
    update_user(user_id=message.from_user.id, last_name=message.text.strip())
    await state.clear()
    await message.answer("Фамилия обновлена \u2705", reply_markup=menu_main)

@router.callback_query(F.data == "edit_username")
async def update_username(callback: CallbackQuery):
    username = callback.from_user.username
    if not username:
        await callback.message.answer("\u274c Не удалось получить username из Telegram.")
    else:
        update_user(user_id=callback.from_user.id, username=username)
        await callback.message.answer("Никнейм обновлён \u2705", reply_markup=menu_main)
    await callback.answer()

@router.callback_query(F.data == "edit_phone")
async def update_phone(update: CallbackQuery | Message, state: FSMContext):
    await state.set_state(StateEditProfile.phone)

    if isinstance(update, CallbackQuery):
        await update.message.answer(
            "Отправьте контакт, нажав кнопку, или введите номер телефона вручную в формате 79123456789:",
            reply_markup=menu_edit_request_contact
        )
        await update.answer()
    elif isinstance(update, Message):
        await update.answer(
            "Отправьте контакт, нажав кнопку, или введите номер телефона вручную в формате 79123456789:",
            reply_markup=menu_edit_request_contact
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

    update_user(user_id=message.from_user.id, phone=phone)
    await state.clear()
    await message.answer("Телефон обновлён \u2705", reply_markup=menu_main)


# @router.callback_query(F.data == "edit_all")
# async def edit_all_fields(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(EditProfile.first_name)
#     await callback.message.answer("Введите имя:")
#     await callback.answer()


# @router.message(EditProfile.first_name)
# async def edit_all_step1(message: Message, state: FSMContext):
#     await state.update_data(first_name=message.text.strip())
#     await state.set_state(EditProfile.last_name)
#     await message.answer("Введите фамилию:")


# @router.message(EditProfile.last_name)
# async def edit_all_step2(message: Message, state: FSMContext):
#     await state.update_data(last_name=message.text.strip())
#     await state.set_state(EditProfile.phone)
#     await message.answer("Введите номер телефона:")


# @router.message(EditProfile.phone)
# async def edit_all_step3(message: Message, state: FSMContext):
#     await state.update_data(phone=message.text.strip())
#     username = message.from_user.username
#     data = await state.get_data()

#     update_user(
#         user_id=message.from_user.id,
#         first_name=data.get("first_name"),
#         last_name=data.get("last_name"),
#         phone=data.get("phone"),
#         username=username
#     )

#     await state.clear()
#     await message.answer("Профиль полностью обновлён \u2705")
