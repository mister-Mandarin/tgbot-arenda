import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook
from dotenv import load_dotenv

from db.database import init_db
from handlers import reservation, start
from handlers.admin import admin_broadcast, admin_init
from handlers.profile import edit, view
from services.middleware import TrackUserActivityMiddleware

load_dotenv()


async def main():
    init_db()

    token = os.getenv("BOT_TOKEN")

    if not token:
        logging.error("BOT_TOKEN не найден в переменных окружения")
        sys.exit(1)

    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot(DeleteWebhook(drop_pending_updates=True))

    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(admin_init.admin_router)
    dp.include_router(admin_broadcast.admin_router)
    dp.include_router(view.router)
    dp.include_router(edit.router)
    dp.include_router(reservation.router)
    dp.update.outer_middleware(TrackUserActivityMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        if os.getenv("APP_ENV") == "dev":
            logging.basicConfig(
                level=logging.INFO,
                stream=sys.stdout,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
        print("Bot started...")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
