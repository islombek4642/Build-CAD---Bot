
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from dotenv import load_dotenv
from config import settings
from bot import handlers

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN', settings.TELEGRAM_BOT_TOKEN)
    if not token:
        logging.error('TELEGRAM_BOT_TOKEN not set!')
        print("\n[ERROR] TELEGRAM_BOT_TOKEN kiritilmagan.\n")
        print(".env faylini to‘ldiring. BotFather’dan token oling va .env faylga quyidagicha yozing:")
        print("TELEGRAM_BOT_TOKEN=your_token_here")
        print("\nBotni ishga tushirish uchun .env faylni to‘ldirib, run.py ni qayta ishga tushiring.")
        return

    from aiogram.client.bot import DefaultBotProperties
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    router = Router()

    router.message.register(handlers.start, Command("start"))
    router.message.register(handlers.process_dims, handlers.Questionnaire.land_dims)
    router.message.register(handlers.process_floors, handlers.Questionnaire.floors)
    router.message.register(handlers.process_rooms, handlers.Questionnaire.rooms)
    router.message.register(handlers.process_notes_and_gen, handlers.Questionnaire.notes)
    router.message.register(handlers.handle_message)
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
