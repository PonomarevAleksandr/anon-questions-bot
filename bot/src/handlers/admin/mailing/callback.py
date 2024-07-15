from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.callbacks import AdminMailing, SendMailing, AdminPanel
from src.utils.db import MongoDbClient
from src.utils.fsm_state import Mailing

router = Router()


# Handler for starting the mailing process
@router.callback_query(AdminMailing.filter())
async def mailing_start(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer('✉️ Mailing')
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    # Prompt the user to enter the text for the mailing
    mes = await bot.edit_message_text(chat_id=callback_query.from_user.id, text='Enter text for mailing:',
                                      message_id=callback_query.message.message_id, reply_markup=keyboard.as_markup())
    await state.set_state(Mailing.mailing_send)
    await state.update_data(message_id=mes.message_id)


# Handler for confirming and sending the mailing to all users
@router.callback_query(SendMailing.filter())
async def send_all_confirm(callback_query: CallbackQuery, db: MongoDbClient,
                           callback_data: SendMailing, bot: Bot):
    await callback_query.answer('✅ Confirm')
    users = await db.users.find({}, count=1)
    users_list = [{'id': user.id} for user in users]
    successful_sends = 0
    failed_sends = 0
    # Notify the user that the mailing process may take a long time
    mes = await bot.send_message(chat_id=callback_query.from_user.id,
                                 text=f'Please wait, this may take a long time...')
    for user in users_list:
        try:
            # Try to send the message to each user
            await bot.copy_message(chat_id=int(user['id']), from_chat_id=callback_query.from_user.id,
                                   message_id=int(callback_data.mes_id), parse_mode='html')
            successful_sends += 1
        except:
            failed_sends += 1
        print(f'Trying to send mailing: {int(successful_sends + failed_sends)} out of {len(users_list)}')

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mes.message_id)
    # Notify the user of the mailing results
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=f'Mailing sent!\nTotal users: {len(users_list)}\n'
                                f'Successful: {successful_sends}\nFailed: {failed_sends}',
                           reply_markup=keyboard.as_markup())
