from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.callbacks import AdminMailing, SendMailing
from src.utils.fsm_state import Mailing

router = Router()


# Handler for confirming the mailing text before sending
@router.message(Mailing.mailing_send)
async def confirm_mailing(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    builder_accept = InlineKeyboardBuilder()
    builder_accept.row(InlineKeyboardButton(
        text='✅ Confirm', callback_data=SendMailing(mes_id=message.message_id).pack()))
    builder_accept.row(InlineKeyboardButton(
        text='❌ Cancel', callback_data=AdminMailing().pack()))
    # Prompt the user to check the mailing text before sending
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=int(data.get('message_id')),
                                text=f'Check the mailing text before sending:\n\n{message.text}',
                                parse_mode='html', reply_markup=builder_accept.as_markup())

    await state.clear()
