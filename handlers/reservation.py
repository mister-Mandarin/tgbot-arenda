from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from keyboards.reservation import menu_hall_check
from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, get_user_locale
from aiogram.filters.callback_data import CallbackData
from services.helpers import LIST_HALLS
from datetime import datetime

router = Router()
now = datetime.now()

class StateReservation(StatesGroup):
    hall = State()
    date = State()
    time_start = State()
    time_end = State()

@router.message(F.text == "📋 Забронировать зал")
async def show_profile(message: Message,state: FSMContext):
    await message.answer("📋 Начинаю процесс бронирования зала.\n\nПосле завершения, отправим контакты вашего профиля менеджеру. Он свяжется с вами для подтвержения броинирования и оплаты.", reply_markup=ReplyKeyboardRemove())
    await message.answer(f'1/4 🔵⚪⚪⚪\n\nВыберите зал для бронирования: 👇', reply_markup=menu_hall_check)
    await state.set_state(StateReservation.hall)

@router.callback_query(F.data.startswith("check_"))
async def choose_hall(callback: CallbackQuery, state: FSMContext):
    hall_alias = callback.data.replace("check_", "")
    hall = [h for h in LIST_HALLS if h["alias"] == hall_alias][0]

    await callback.message.answer("✅ Вы выбрали зал: " + hall["name"])
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(hall=hall_alias)
    await callback.message.answer(f'2/4 🔵🔵⚪⚪\n\nТеперь выберите дату: ',
        reply_markup=await SimpleCalendar(locale=await get_user_locale(callback.from_user)).start_calendar()
    )
    await state.set_state(StateReservation.date)

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user), show_alerts=True)
    
    calendar.set_dates_range(datetime.now(), datetime(now.year + 1, now.month, now.day))
    selected, date = await calendar.process_selection(callback_query, callback_data)

    if selected:
        date = date.strftime("%Y-%m-%d")
        await state.update_data(date=date)
        await callback_query.message.answer(f'✅ Дата мероприятия: {date}')
        await state.set_state(StateReservation.time_start)

@router.message(StateReservation.time_start)
async def process_time_start(message: Message, state: FSMContext):
    await message.answer("Введите время начала мероприятия в формате 10:00: ")
    await state.set_state(StateReservation.time_end)
