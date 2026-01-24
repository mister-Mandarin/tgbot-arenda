from datetime import date, datetime

from aiogram import Bot, F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from db.user import get_user
from handlers.admin.admin_init import notify_admins
from handlers.callback_factory import SelectTimeEndCallback, SelectTimeStartCallback
from keyboards.menu import menu_main
from keyboards.reservation import (
    menu_hall_change_date,
    menu_hall_check,
    menu_hall_confirm,
    menu_hall_time,
)
from services.helpers import LIST_HALLS, create_reservation_text, get_state
from services.time_slots import generate_free_time_end, generate_free_time_start

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


async def process_time_start(callback: CallbackQuery, state: FSMContext):
    """Свободное время начала"""
    data = await get_state(state, "free_time_start")
    await callback.message.answer(
        (
            "3/4 🔵🔵🔵⚪\n\n"
            "Время вам подбирается автоматически с учётом следующих условий:\n"
            "Минимальная продолжительность бронирования 1 час. 🕐\n"
            "Центр работа с 10:00 до 22:00 каждый день.\n"
            "В одном зале в одно время может проходить только одно мероприятие.\n"
            "Выберите свободное время начала мероприятия 👇\n"
        ),
        reply_markup=menu_hall_time(data),
    )


async def process_time_end(callback: CallbackQuery, state: FSMContext):
    data = await get_state(state, "free_time_end")
    await callback.message.answer(
        ("4/4 🔵🔵🔵🔵\n\nВыберите дату окончания мероприятия 👇"),
        reply_markup=menu_hall_time(data, is_end=True),
    )
    await state.set_state(StateReservation.time_end)


async def show_reservation_summary(callback: CallbackQuery, state: FSMContext):
    """Показать итог бронирования"""
    data = await state.get_data()
    user_data = await get_user(callback.from_user.id)

    if user_data is None:
        user_data = {
            "first_name": callback.from_user.first_name,
            "last_name": callback.from_user.last_name,
            "phone": "-",
            "username": callback.from_user.username,
        }

    reservation_text = create_reservation_text(data, user_data)

    text = (
        "<b>Сводка вашего бронирования:</b>\n\n"
        f"{reservation_text}"
        "\n"
        "<i>Пожалуйста, проверьте данные.\n</i>"
        "<i>Если всё верно — подтвердите бронирование.</i>"
    )

    await callback.message.answer(text, reply_markup=menu_hall_confirm)


async def calendar_markup() -> InlineKeyboardMarkup:
    """Формирование клавиатуры с датами"""
    today = date.today()

    if today in _calendar_cache:
        return _calendar_cache[today]

    calendar = await SimpleCalendar().start_calendar()
    _calendar_cache[today] = calendar

    return calendar


@router.message(F.text == "📋 Выбрать другую дату")
async def process_date(update: CallbackQuery | Message, state: FSMContext):
    """Выбор даты. Календарь"""
    calendar = await calendar_markup()

    if isinstance(update, Message):
        await update.answer("2/4 🔵🔵⚪⚪\n\nВыберите дату: ", reply_markup=calendar)

    if isinstance(update, CallbackQuery):
        await update.message.answer(
            "2/4 🔵🔵⚪⚪\n\nВыберите дату: ", reply_markup=calendar
        )

    await state.set_state(StateReservation.date)


@router.message(F.text.in_(["📋 Забронировать зал", "✏️ Изменить бронь"]))
async def show_profile(message: Message, state: FSMContext):
    """Выбор зала для бронирования, кнопки"""
    await message.answer(
        "📋 Начинаю процесс бронирования зала.", reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "1/4 🔵⚪⚪⚪\n\nВыберите зал: 👇", reply_markup=menu_hall_check
    )
    await state.set_state(StateReservation.hall)


@router.callback_query(F.data.startswith("check_"))
async def choose_hall(callback: CallbackQuery, state: FSMContext):
    """Запись выбранного зала"""
    hall_alias = callback.data.replace("check_", "")
    hall = [h for h in LIST_HALLS if h["alias"] == hall_alias][0]

    await callback.message.answer("✅ Вы выбрали зал: " + hall["name"])
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(hall=hall)
    await process_date(callback, state)


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext
):
    """Обработка выбранной даты."""
    calendar = SimpleCalendar()

    calendar.set_dates_range(datetime.now(), datetime(now.year + 1, now.month, now.day))
    selected, selected_date = await calendar.process_selection(
        callback_query, callback_data
    )

    if selected:
        data = await get_state(state, "hall")

        format_selected_date = selected_date.strftime("%Y-%m-%d")
        free_time_start, clear_buzy_time = await generate_free_time_start(
            data["alias"], format_selected_date
        )

        if len(free_time_start) == 0:
            await callback_query.answer(
                "⚠️⚠️⚠️\n"
                "Упс... На эти даты свободных мест нет.\n\n"
                "Пожалуйста выберите другую дату 👇",
                show_alert=True,
            )
            calendar = await calendar_markup()
            await callback_query.message.edit_text(
                "2/4 🔵🔵⚪⚪\n\nПожалуйста выберите другую дату:",
                reply_markup=calendar,
            )
            return

        await state.update_data(date=format_selected_date)
        await callback_query.message.answer(
            f"✅ Дата мероприятия: {format_selected_date}",
            reply_markup=menu_hall_change_date,
        )
        await state.update_data(
            free_time_start=free_time_start, clear_buzy_time=clear_buzy_time
        )
        await process_time_start(callback_query, state)


@router.callback_query(SelectTimeStartCallback.filter())
async def handle_time_selected_start(
    callback: CallbackQuery, callback_data: SelectTimeStartCallback, state: FSMContext
):
    selected_time = callback_data.value.replace("-", ":")
    await state.update_data(time_start=selected_time)

    data = await get_state(state, "clear_buzy_time")
    free_time_end = await generate_free_time_end(selected_time, data)

    await state.update_data(free_time_end=free_time_end)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Вы выбрали время начала: {selected_time}")
    await process_time_end(callback, state)


@router.callback_query(SelectTimeEndCallback.filter())
async def handle_time_selected_end(
    callback: CallbackQuery, callback_data: SelectTimeEndCallback, state: FSMContext
):
    selected_time = callback_data.value.replace("-", ":")
    await state.update_data(time_end=selected_time)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Вы выбрали время заверешния: {selected_time}")
    await show_reservation_summary(callback, state)


@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    """Обработчик кнопки отмена"""
    await state.clear()
    await message.answer(
        text="❌ Бронирование отменено. Вы вернулись в главное меню.",
        reply_markup=menu_main,
    )


@router.message(F.text == "✅ Подтвердить бронирование")
async def confirm_reservation(message: Message, state: FSMContext, bot: Bot):
    """Обработчик подтверждения бронирования и уведомления админов"""
    await message.answer(
        "✅ Данные бронирования отправлены!\n\n"
        "В ближайшее время с вами свяжется менеджер Альфа-Зет для подтверждения. 😊",
        reply_markup=menu_main,
    )

    data = await state.get_data()
    user_data = await get_user(message.from_user.id)
    reservation_text = create_reservation_text(data, user_data)

    await notify_admins(reservation_text, bot)

    await state.clear()
