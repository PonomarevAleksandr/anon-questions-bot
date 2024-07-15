from typing import Union

from pydantic import BaseModel


class User(BaseModel):
    id: int
    is_bot: bool
    refer_id: Union[int, None] = None
    first_start: Union[bool, None] = True
    first_name: str
    adv_id: Union[int, None] = 1
    last_name: Union[str, None] = None
    username: Union[str, None] = None
    language_code: Union[str, None] = None
    is_premium: Union[bool, None] = None
    added_to_attachment_menu: Union[bool, None] = None
    can_join_groups: Union[bool, None] = None
    can_read_all_group_messages: Union[bool, None] = None
    supports_inline_queries: Union[bool, None] = None
    created_at: int = 0
    updated_at: int = 0
    blocked_at: Union[int, None] = None
