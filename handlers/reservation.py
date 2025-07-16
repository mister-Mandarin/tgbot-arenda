from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from keyboards.reservation import menu_hall_check, menu_hall_time, menu_hall_confirm
from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.filters.callback_data import CallbackData
from services.helpers import LIST_HALLS, get_state
from datetime import date, datetime
from services.time_slots import generate_free_time_start, generate_free_time_end
from .callback_factory import SelectTimeStartCallback, SelectTimeEndCallback
from keyboards.reservation import menu_hall_change_date
from db.user import get_user
from keyboards.menu import menu_main
from handlers.admin import notify_admins

router = Router()
now = datetime.now()
_calendar_cache: dict[date, InlineKeyboardMarkup] = {}

class StateReservation(StatesGroup):
    hall = State()
    date = State()
    clear_buzy_time = State()
    free_time_start = State()
    free_time_end = State()
    time_start = State()
    time_end = State()
    reservation_text = State()

'''
Свободное время начала
'''
async def process_time_start(callback: CallbackQuery, state: FSMContext):
    data = await get_state(state, 'free_time_start')
    await callback.message.answer((
                            f'3/4 🔵🔵🔵⚪\n\n'
                            f'Время вам подбирается автоматически с учётом следующих условий:\n'
                            f'Минимальная продолжительность бронирования 1 час. 🕐\n'
                            f'Центр работа с 10:00 до 22:00 каждый день.\n'
                            f'В одном зале в одно время может проходить только одно мероприятие.\n'
                            f'Выберите свободное время начала мероприятия 👇\n'
                        ), reply_markup = menu_hall_time(data))

async def process_time_end(callback: CallbackQuery, state: FSMContext):
    data = await get_state(state,'free_time_end')
    await callback.message.answer((
                            f'4/4 🔵🔵🔵🔵\n\n'
                            f'Выберите дату окончания мероприятия 👇'
                        ), reply_markup=menu_hall_time(data, is_end=True))
    await state.set_state(StateReservation.time_end)

async def show_reservation_summary(callback: CallbackQuery, state: FSMContext):
    data = await get_state(state)
    user_data = get_user(callback.from_user.id)

    text = (
        "<b>Ваша бронь:</b>\n"
        f"🏛️ Зал: <b>{data.get('hall', {}).get('name', '-')}</b>\n"
        f"📅 Дата: <b>{data.get('date', '—')}</b>\n"
        f"🕒 Время начала: <b>{data.get('time_start', '—')}</b>\n"
        f"🕔 Время окончания: <b>{data.get('time_end', '—')}</b>\n"
        f"\n\n"
        f"<b>Контактрые данные:</b>\n"
        f"🧑 Имя: {user_data['first_name']}\n"
        f"👥 Фамилия: {user_data['last_name'] or '-'}\n"
        f"📱 Телефон: {user_data['phone'] or '-'}\n"
        f"📛 Никнейм: @{user_data['username'] if user_data['username'] else '-'}\n"
    )

    await state.update_data(reservation_text=text)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=menu_hall_confirm)

'''
Формирование клавиатуры с датами
'''
async def calendar_markup() -> InlineKeyboardMarkup:
    today = date.today()

    if today in _calendar_cache:
        return _calendar_cache[today]

    calendar = await SimpleCalendar().start_calendar()
    _calendar_cache[today] = calendar

    return calendar
    
'''
Выбор даты. Календарь
'''
@router.message(F.text == "📋 Выбрать другую дату")
async def process_date(update: CallbackQuery | Message, state: FSMContext):
    calendar = await calendar_markup()

    if isinstance(update, Message):
        await update.answer(f'2/4 🔵🔵⚪⚪\n\nВыберите дату: ', reply_markup=calendar)

    if isinstance(update, CallbackQuery):
        await update.message.answer(f'2/4 🔵🔵⚪⚪\n\nВыберите дату: ', reply_markup=calendar)
    
    await state.set_state(StateReservation.date)

'''
Выбор зала для бронирования, кнопки
'''
@router.message(F.text.in_(["📋 Забронировать зал", "✏️ Изменить бронь"]))
async def show_profile(message: Message, state: FSMContext):
    await message.answer("📋 Начинаю процесс бронирования зала.", reply_markup=ReplyKeyboardRemove())
    await message.answer(f'1/4 🔵⚪⚪⚪\n\nВыберите зал: 👇', reply_markup=menu_hall_check)
    await state.set_state(StateReservation.hall)

'''
Запись выбранного зала
'''
@router.callback_query(F.data.startswith("check_"))
async def choose_hall(callback: CallbackQuery, state: FSMContext):
    hall_alias = callback.data.replace("check_", "")
    hall = [h for h in LIST_HALLS if h["alias"] == hall_alias][0]

    await callback.message.answer("✅ Вы выбрали зал: " + hall["name"])
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(hall=hall)
    await process_date(callback, state)

'''
Обработка выбранной даты.
'''
@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar()

    calendar.set_dates_range(datetime.now(), datetime(now.year + 1, now.month, now.day))
    selected, selected_date = await calendar.process_selection(callback_query, callback_data)

    if selected:
        data = await get_state(state, "hall")

        date = selected_date.strftime("%Y-%m-%d")
        free_time_start, clear_buzy_time = generate_free_time_start(data["alias"], date)

        if len(free_time_start) == 0:
            await callback_query.answer(
                f'⚠️⚠️⚠️\n'
                f'Упс... На эти даты свободных мест нет.\n\n'
                f'Пожалуйста выберите другую дату 👇',
                show_alert=True
            )
            calendar = await calendar_markup()
            await callback_query.message.edit_text(
                f'2/4 🔵🔵⚪⚪\n\nПожалуйста выберите другую дату:',
                reply_markup=calendar
            )
            return
        
        await state.update_data(date=date)
        await callback_query.message.answer(f'✅ Дата мероприятия: {date}', reply_markup=menu_hall_change_date)
        await state.update_data(free_time_start=free_time_start, clear_buzy_time=clear_buzy_time)
        await process_time_start(callback_query, state)

@router.callback_query(SelectTimeStartCallback.filter())
async def handle_time_selected(callback: CallbackQuery, callback_data: SelectTimeStartCallback, state: FSMContext):
    selected_time = callback_data.value.replace("-", ":")
    await state.update_data(time_start=selected_time)

    data = await get_state(state, "clear_buzy_time")
    free_time_end = generate_free_time_end(selected_time, data)

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

'''
Обработчик кнопки отмена
'''
@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="❌ Бронирование отменено. Вы вернулись в главное меню.",
        reply_markup=menu_main
    )


'''
Обработчик подтверждения бронирования
и уведомления админов
'''
@router.message(F.text == "✅ Подтвердить бронирование")
async def confirm_reservation(message: Message, state: FSMContext):
    await message.answer(
        '✅ Данные бронирования отправлены!\n\n'
        '📞 В ближайшее время с вами свяжется менеджер Альфа-Зет для подтверждения. 😊',
        reply_markup=menu_main
    )

    await notify_admins(message, state)

    await state.clear()