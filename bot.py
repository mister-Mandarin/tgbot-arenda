import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook

from handlers import start, reservation
from handlers.profile import view, edit
from db.database import init_db
from dotenv import load_dotenv

load_dotenv()

async def main():
    init_db()
    bot = Bot(os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot(DeleteWebhook(drop_pending_updates=True))

    dp = Dispatcher()
    dp.include_router(start.router)
    #dp.include_router(admin.router)
    dp.include_router(view.router)
    dp.include_router(edit.router)
    dp.include_router(reservation.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if os.getenv("APP_ENV") == "dev":
            logging.basicConfig(
                level=logging.INFO,
                stream=sys.stdout,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        else:
            logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")