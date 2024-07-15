from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from cachetools import TTLCache

caches = {
    "default": TTLCache(maxsize=10_000, ttl=0.1)
}


class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:

        if event.from_user.id in caches['default']:
            return
        else:
            caches['default'][event.from_user.id] = None
        return await handler(event, data)
