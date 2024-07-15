from aiogram.fsm.state import StatesGroup, State


class SendMessage(StatesGroup):
    send_message = State()


class ReplyMessage(StatesGroup):
    reply_message = State()


class AddSponsorFSM(StatesGroup):
    send_name = State()
    send_url = State()
    send_chanel_id = State()


class EditSponsorFSM(StatesGroup):
    edit_name = State()
    edit_url = State()
    edit_chanel_id = State()


class Mailing(StatesGroup):
    mailing_send = State()


class SendAdv(StatesGroup):
    send_adv = State()


class EditMedia(StatesGroup):
    edit_media = State()


class EditText(StatesGroup):
    edit_text = State()
