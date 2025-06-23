import asyncio
import os
from aiogram import Bot, Dispatcher
from handlers import start
from db.database import init_db
from handlers.profile import view, edit

async def main():
    init_db()
    bot = Bot(os.environ['BOT_TOKEN'])
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(view.router)
    dp.include_router(edit.router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
