from typing import Union

from pydantic import BaseModel


class Referrals(BaseModel):
    id: str
    link: str
    clicks: Union[int, None] = 0

