import calendar
import locale

from aiogram.types import User
from datetime import datetime

from .schemas import CalendarLabels


async def get_user_locale(from_user: User) -> str:
    "Returns user locale in format en_US, accepts User instance from Message, CallbackData etc"
    loc = from_user.language_code
    return locale.locale_alias[loc].split(".")[0]


class GenericCalendar:

    def __init__(
        self,
        locale: str = 'ru_RU',
        cancel_btn: str = None,
        today_btn: str = None,
        show_alerts: bool = True
    ) -> None:
        """Pass labels if you need to have alternative language of buttons

        Parameters:
        locale (str): Locale calendar must have captions in (in format uk_UA), if None - default English will be used
        cancel_btn (str): label for button Cancel to cancel date input
        today_btn (str): label for button Today to set calendar back to todays date
        show_alerts (bool): defines how the date range error would shown (defaults to False)
        """
        self._labels = CalendarLabels()
        if locale:
            # getting month names and days of week in specified locale
            with calendar.different_locale(locale):
                self._labels.days_of_week = list(calendar.day_abbr)
                self._labels.months = calendar.month_abbr[1:]

        if cancel_btn:
            self._labels.cancel_caption = cancel_btn
        if today_btn:
            self._labels.today_caption = today_btn

        self.min_date = None
        self.max_date = None
        self.show_alerts = show_alerts

    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """Sets range of minimum & maximum dates"""
        self.min_date = min_date
        self.max_date = max_date

    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f'⚠️⚠️⚠️\n'
                f'Вы пытаетесь выбрать дату раньше чем текущая {self.min_date.strftime("%d/%m/%Y")}.\n\n'
                f'Путешествия во времени пока не возможны. Пожалуйста выберите другую дату 👇',
                show_alert=True
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'The date have to be before {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date
