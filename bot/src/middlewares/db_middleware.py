from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from motor.motor_asyncio import AsyncIOMotorClient



class DataBaseMiddleware(BaseMiddleware):
    def __init__(self, db: AsyncIOMotorClient):
        super().__init__()
        self.db = db

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        data["db"] = self.db
        return await handler(event, data)
