from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.helpers import ADMIN_IDS


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        return message.from_user.id in ADMIN_IDS
