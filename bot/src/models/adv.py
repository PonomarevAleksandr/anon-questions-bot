from typing import Union

from pydantic import BaseModel


class Adv(BaseModel):
    adv_id: Union[int, None]
    caption: Union[str, None]
    content_type: Union[str, None]
    content: Union[str, None]
    date: Union[float, None]


