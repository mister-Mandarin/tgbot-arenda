import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import start
from handlers.profile import view, edit
from handlers import reservation
from db.database import init_db
from dotenv import load_dotenv

load_dotenv()

async def main():
    init_db()
    bot = Bot(os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(view.router)
    dp.include_router(edit.router)
    dp.include_router(reservation.router)

    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")