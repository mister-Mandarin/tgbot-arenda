from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from cachetools import TTLCache

from db.user import set_user_active_true

# 1000 записей
# ttl время хранения 1 день
active_users_cache = TTLCache(maxsize=1000, ttl=86400)


class TrackUserActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")

        if user:
            # Проверяем, есть ли юзер в кэше
            if user.id not in active_users_cache:
                active_users_cache[user.id] = True
                await set_user_active_true(user.id)

        return await handler(event, data)
