import os
import logging

import asyncio
from aiogram import Dispatcher, Bot
from aiogram.client.session.aiohttp import AiohttpSession

from config import load_env
from src.utils.db import db

from src.handlers import router as main_router
from src.middlewares.db_middleware import DataBaseMiddleware
from src.middlewares.throttling_middleware import ThrottlingMiddleware
from src.middlewares.user_middleware import UserMiddleware

logging.basicConfig(level=logging.INFO)
load_env()


async def main():
    session = AiohttpSession()
    bot_settings = {"session": session, "parse_mode": "HTML"}
    bot = Bot(token=os.getenv("BOT_TOKEN"), **bot_settings)
    dp = Dispatcher()

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.outer_middleware(DataBaseMiddleware(db=db))
    dp.message.outer_middleware(UserMiddleware())
    # ---
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.callback_query.outer_middleware(DataBaseMiddleware(db=db))
    dp.callback_query.outer_middleware(UserMiddleware())

    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
