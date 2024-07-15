from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.callbacks import AddSponsor, ChannelSelect, AdminPanel
from src.utils.db import MongoDbClient
from src.utils.fsm_state import AddSponsorFSM, EditSponsorFSM
from src.utils.functions.admin.function import update_channel_data, edit_message, build_keyboard

router = Router()


# Handler for changing the sponsor's name
@router.message(EditSponsorFSM.edit_name)
async def change_name(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    # Update the channel's name in the database
    await update_channel_data(db, {'channel_id': int(data.get('channel_id'))},
                              {'name': message.text})
    # Build the keyboard for the updated channel
    keyboard = build_keyboard(int(data.get('channel_id')))
    # Edit the message to display the updated channel's information
    await edit_message(bot, message.from_user.id, int(data.get('message_id')),
                       f'Sponsor: {message.text}\n\nUrl: {data.get("url")}\n'
                       f'Channel_id: {data.get("channel_id")}\n\nSubscribed: {data.get("subs")}',
                       keyboard)
    await state.clear()


# Handler for changing the channel's ID
@router.message(EditSponsorFSM.edit_chanel_id)
async def change_channel_id(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    # Update the channel's ID in the database
    await update_channel_data(db, {'channel_id': int(data.get('channel_id'))},
                              {'channel_id': int(message.text)})
    # Build the keyboard for the updated channel
    keyboard = build_keyboard(int(message.text))
    # Edit the message to display the updated channel's information
    await edit_message(bot, message.from_user.id, int(data.get('message_id')),
                       f'Sponsor: {data.get("name")}\n\nUrl: {data.get("url")}\n'
                       f'Channel_id: {message.text}\n\nSubscribed: {data.get("subs")}',
                       keyboard)
    await state.clear()


# Handler for changing the channel's URL
@router.message(EditSponsorFSM.edit_url)
async def change_url(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    # Update the channel's URL in the database
    await update_channel_data(db, {'channel_id': int(data.get('channel_id'))},
                              {'url': message.text.replace(':', ';')})
    # Build the keyboard for the updated channel
    keyboard = build_keyboard(int(data.get('channel_id')))
    # Edit the message to display the updated channel's information
    await edit_message(bot, message.from_user.id, int(data.get('message_id')),
                       f'Sponsor: {data.get("name")}\n\nUrl: {message.text}\n'
                       f'Channel_id: {data.get("channel_id")}\n\nSubscribed: {data.get("subs")}',
                       keyboard)
    await state.clear()


# Handler for uploading the sponsor's name
@router.message(AddSponsorFSM.send_name)
async def upload_name(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    # Prompt the user to enter the channel's ID
    res = await bot.edit_message_text(chat_id=message.from_user.id, text='Enter channel ID:',
                                      message_id=int(data.get('message_id')))
    await state.set_state(AddSponsorFSM.send_chanel_id)
    await state.update_data(message_id=res.message_id, name=message.text)


# Handler for uploading the channel's ID
@router.message(AddSponsorFSM.send_chanel_id)
async def upload_channel_id(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    # Prompt the user to enter the channel's URL
    res = await bot.edit_message_text(chat_id=message.from_user.id, text='Enter channel URL:',
                                      message_id=int(data.get('message_id')))
    await state.set_state(AddSponsorFSM.send_url)
    await state.update_data(message_id=res.message_id, name=data.get('name'), channel_id=message.text)


# Handler for uploading the channel's URL
@router.message(AddSponsorFSM.send_url)
async def upload_url(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    # Insert the new channel into the database
    await db.channels.insert_one({'channel_id': int(data.get('channel_id')), 'name': str(data.get('name')),
                                  'url': str(message.text.replace(':', ';'))})
    # Retrieve all channels from the database
    channels = await db.channels.find({})
    channels_list = [{'channel_id': channel.channel_id, 'url': channel.url, 'name': channel.name} for channel in
                     channels]
    markup = InlineKeyboardBuilder()
    # Add each channel to the inline keyboard
    for channel in channels_list:
        markup.row(InlineKeyboardButton(text=channel['name'],
                                        callback_data=ChannelSelect(channel_id=channel['channel_id']).pack()))
    # Add buttons for adding a sponsor and going back to the admin panel
    markup.row(InlineKeyboardButton(text='Add Sponsor', callback_data=AddSponsor(edit='no').pack()))
    markup.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    # Edit the message to display the channels
    await bot.edit_message_text(chat_id=message.from_user.id, text="Channels:", reply_markup=markup.as_markup(),
                                message_id=int(data.get('message_id')))
    await state.clear()
