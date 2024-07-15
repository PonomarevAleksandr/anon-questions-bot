from typing import Optional

from aiogram.filters.callback_data import CallbackData


# -- User
class Reply(CallbackData, prefix='reply'):
    sender: int
    action: str
    reply_message: int
    referer: int


class GetLink(CallbackData, prefix='get_link'):
    referer: int
    check_my: bool


class SendAgain(CallbackData, prefix='send_again'):
    referer: int
    action: str


# -- Admin

class AdminStats(CallbackData, prefix='admin_stats'):
    ...


class AdminUpload(CallbackData, prefix='admin_upload'):
    ...


class AdminMailing(CallbackData, prefix='admin_mailing'):
    ...


class AdminChannels(CallbackData, prefix='admin_channels'):
    ...


class AdminRefs(CallbackData, prefix='admin_refs'):
    ...


class AdminAdv(CallbackData, prefix='admin_adv'):
    ...


class AddSponsor(CallbackData, prefix='sponsor'):
    edit: str
    channel_id: Optional[int] = None


class RemoveSponsor(CallbackData, prefix='remove_sponsor'):
    channel_id: int


class SponsorList(CallbackData, prefix='list_sponsor'):
    ...


class ChannelSelect(CallbackData, prefix='ChannelSelect'):
    channel_id: int


class Start(CallbackData, prefix='start'):
    message: str


class AdminPanel(CallbackData, prefix='admin_panel'):
    ...


class SendMailing(CallbackData, prefix='send_mailing'):
    mes_id: int


class AddReferral(CallbackData, prefix='referral'):
    ...


class RemoveReferral(CallbackData, prefix='remove_referral'):
    id: str


class ReferralList(CallbackData, prefix='list_referral'):
    ...


class ReferralSelect(CallbackData, prefix='referral_select'):
    id: str


class AddAdv(CallbackData, prefix='add_adv'):
    ...


class AdvNav(CallbackData, prefix='adv_nav'):
    index: int


class AdvRemove(CallbackData, prefix='adv_remove'):
    adv_id: int


class AdvEdit(CallbackData, prefix='adv_edit'):
    adv_id: int


class AdvMediaEdit(CallbackData, prefix='adv_edit_media'):
    adv_id: int


class AdvTextEdit(CallbackData, prefix='adv_edit_text'):
    adv_id: int
