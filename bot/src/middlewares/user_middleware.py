import time
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict

from aiogram import BaseMiddleware
from aiogram.types import Update, Message

from src.models.user import User


class UserMiddleware(BaseMiddleware):

    def __init__(self) -> None:
        pass

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if not hasattr(event, 'from_user'):
            return

        user = await data['db'].users.find_one(f={'id': event.from_user.id})

        if isinstance(event, Message):

            if user is None:
                if hasattr(event, 'text'):

                    new_user = event.from_user.model_dump()
                    new_user['created_at'] = int(time.time())
                    new_user['updated_at'] = int(time.time())

                    try:
                        if 'rl' in event.text:
                            new_user['refer_id'] = int(event.text.replace('rl', ''))
                    except:  # noqa
                        ...

                    user = User(**new_user)
                    await data['db'].users.insert_one(user.model_dump())

            else:
                if user.blocked_at is not None:
                    await data['db'].users.update_one({'chat_id': event.from_user.id}, {'blocked_at': None})

        if user.updated_at < time.time() - 300:
            await data['db'].users.update_one({'chat_id': event.from_user.id}, event.from_user.model_dump())

        data['user'] = user
        return await handler(event, data)
