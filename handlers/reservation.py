import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from keyboards.reservation import menu_hall_check, menu_hall_time
from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from aiogram.filters.callback_data import CallbackData
from services.helpers import LIST_HALLS
from datetime import datetime
from services.time_slots import generate_free_time_start, generate_free_time_end
from .callback_factory import SelectTimeStartCallback, SelectTimeEndCallback

router = Router()
now = datetime.now()

class StateReservation(StatesGroup):
    hall = State()
    date = State()
    clear_buzy_time = State()
    free_time_start = State()
    free_time_end = State()
    time_start = State()
    time_end = State()

async def process_time_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    await callback.message.answer((
                            f'3/4 🔵🔵🔵⚪\n\n'
                            f'Время вам подбирается автоматически с учётом следующих условий:\n'
                            f'Минимальная продолжительность бронирования 1 час. 🕐\n'
                            f'Центр работа с 10:00 до 22:00 каждый день.\n'
                            f'В одном зале в одно времяможет проходить только одно мероприятие.\n'
                            f'Выберите свободное время начала мероприятия 👇\n'
                        ), reply_markup = menu_hall_time(data["free_time_start"]))

async def process_time_end(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer((
                            f'4/4 🔵🔵🔵🔵\n\n'
                            f'Выберите дату окончания мероприятия 👇'
                        ), reply_markup=menu_hall_time(data['free_time_end'], is_end=True))
    await state.set_state(StateReservation.time_end)

async def show_reservation_summary(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = (
        "📝 <b>Ваша бронь:</b>\n"
        f"🏛️ Зал: <b>{data['hall']['name']}</b>\n"
        f"📅 Дата: <b>{data.get('date', '—')}</b>\n"
        f"🕒 Время начала: <b>{data.get('time_start', '—')}</b>\n"
        f"🕔 Время окончания: <b>{data.get('time_end', '—')}</b>\n"
    )
    await callback.message.answer(text, parse_mode="HTML")

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
    await state.update_data(hall=hall)
    calendar = await SimpleCalendar(locale=await get_user_locale(callback.from_user)).start_calendar()

    await callback.message.answer(f'2/4 🔵🔵⚪⚪\n\nТеперь выберите дату: ',
        reply_markup=calendar
    )
    await state.set_state(StateReservation.date)

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(locale=await get_user_locale(callback_query.from_user))
    
    calendar.set_dates_range(datetime.now(), datetime(now.year + 1, now.month, now.day))
    selected, date = await calendar.process_selection(callback_query, callback_data)

    if selected:
        date = date.strftime("%Y-%m-%d")
        await state.update_data(date=date)
        await callback_query.message.answer(f'✅ Дата мероприятия: {date}')
        data = await state.get_data()
        free_time_start, clear_buzy_time = generate_free_time_start(data["hall"]["alias"], date)
        
        await state.update_data(free_time_start=free_time_start, clear_buzy_time=clear_buzy_time)
        await process_time_start(callback_query, state)

@router.callback_query(SelectTimeStartCallback.filter())
async def handle_time_selected(callback: CallbackQuery, callback_data: SelectTimeStartCallback, state: FSMContext):
    selected_time = callback_data.value.replace("-", ":")
    await state.update_data(time_start=selected_time)
    data = await state.get_data()
    free_time_end = generate_free_time_end(selected_time, data["clear_buzy_time"])

    await state.update_data(free_time_end=free_time_end)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Вы выбрали время начала: {selected_time}")
    await process_time_end(callback, state)


@router.callback_query(SelectTimeEndCallback.filter())
async def handle_time_selected(callback: CallbackQuery, callback_data: SelectTimeEndCallback, state: FSMContext):
    selected_time = callback_data.value.replace("-", ":")
    await state.update_data(time_end=selected_time)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Вы выбрали время заверешния: {selected_time}")
    await show_reservation_summary(callback, state)