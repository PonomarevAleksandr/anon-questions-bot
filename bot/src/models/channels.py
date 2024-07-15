from typing import Union

from pydantic import BaseModel


class Channels(BaseModel):
    channel_id: int
    url: str
    name: str
    subs: Union[int, None] = 0
    subscribed_users: Union[list, None] = []

