import logging
from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks import AdminChannels, AddSponsor, RemoveSponsor, SponsorList, ChannelSelect, AdminPanel
from src.utils.db import MongoDbClient
from src.utils.fsm_state import EditSponsorFSM, AddSponsorFSM
from src.utils.functions.admin.function import build_keyboard, edit_message

router = Router()


# Handler for the admin panel callback query
@router.callback_query(AdminChannels.filter())
async def admin_panel(callback_query: CallbackQuery, db: MongoDbClient, bot: Bot):
    # Retrieve all channels from the database
    await callback_query.answer('Channels')  # Send a response to the callback query

    channels = await db.channels.find({})
    channels_list = [{'channel_id': channel.channel_id, 'url': channel.url, 'name': channel.name} for channel in
                     channels]
    markup = InlineKeyboardBuilder()
    await callback_query.answer('Channels')

    # Add each channel to the inline keyboard
    for channel in channels_list:
        markup.row(InlineKeyboardButton(text=channel['name'],
                                        callback_data=ChannelSelect(channel_id=channel['channel_id']).pack()))
    # Add buttons for adding a sponsor and going back to the admin panel
    markup.row(InlineKeyboardButton(text='Add Sponsor', callback_data=AddSponsor(edit='no').pack()))
    markup.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    # Edit the message to display the channels
    await bot.edit_message_text(chat_id=callback_query.from_user.id, text="Channels:",
                                message_id=callback_query.message.message_id, reply_markup=markup.as_markup())


# Handler for the channel selection callback query
@router.callback_query(ChannelSelect.filter())
async def channels_admin(callback_query: CallbackQuery, callback_data: ChannelSelect, bot: Bot, db: MongoDbClient):
    await callback_query.answer('Channel')  # Send a response to the callback query

    # Retrieve the selected channel's information from the database
    info = await db.channels.find_one({'channel_id': int(callback_data.channel_id)})
    await callback_query.answer(info.name)
    # Build the keyboard for the selected channel
    keyboard = build_keyboard(int(callback_data.channel_id))
    # Edit the message to display the selected channel's information
    await edit_message(bot, callback_query.from_user.id, callback_query.message.message_id,
                       f'Sponsor: {info.name}\n\nUrl: {info.url}\nChannel_id: {callback_data.channel_id}\n\n'
                       f'Subscribed: {info.subs}',
                       keyboard)


# Handler for the add sponsor callback query
@router.callback_query(AddSponsor.filter())
async def channels_admin(callback_query: CallbackQuery, callback_data: AddSponsor, bot: Bot, state: FSMContext,
                         db: MongoDbClient):
    await callback_query.answer('Add Sponsor')  # Send a response to the callback query

    try:
        # Retrieve the selected channel's information from the database
        channel_id = await db.channels.find_one({'channel_id': int(callback_data.channel_id)})
    except:
        pass
    await callback_query.answer('Add Sponsor')
    # Edit the message to prompt the user for the sponsor's name, ID, or URL based on the callback data
    if callback_data.edit == 'no':
        res = await bot.edit_message_text(chat_id=callback_query.from_user.id, text='Enter name:',
                                          message_id=callback_query.message.message_id)
        await state.set_state(AddSponsorFSM.send_name)
    elif callback_data.edit == 'name':
        res = await bot.edit_message_text(chat_id=callback_query.from_user.id, text='Enter name:',
                                          message_id=callback_query.message.message_id)
        await state.set_state(EditSponsorFSM.edit_name)
    elif callback_data.edit == 'id':
        res = await bot.edit_message_text(chat_id=callback_query.from_user.id, text='Enter channel ID:',
                                          message_id=callback_query.message.message_id)
        await state.set_state(EditSponsorFSM.edit_channel_id)
    elif callback_data.edit == 'url':
        res = await bot.edit_message_text(chat_id=callback_query.from_user.id, text='Enter URL:',
                                          message_id=callback_query.message.message_id)
        await state.set_state(EditSponsorFSM.edit_url)

    # Update the state with the message ID and channel information if available
    if callback_data.edit == 'no':
        await state.update_data(message_id=res.message_id)  # noqa
    else:
        await state.update_data(channel_id=int(channel_id.channel_id),  # noqa
                                name=channel_id.name, url=channel_id.url, message_id=res.message_id,  # noqa
                                subs=channel_id.subs)  # noqa


# Handler for the sponsor list callback query
@router.callback_query(SponsorList.filter())
async def channels_admin(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient):
    await callback_query.answer('Back')  # Send a response to the callback query

    # Retrieve all channels from the database
    channels = await db.channels.find({})
    await callback_query.answer('Back')
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
    await bot.edit_message_text(chat_id=callback_query.from_user.id, text="Channels:",
                                reply_markup=markup.as_markup(), message_id=callback_query.message.message_id)


# Configure logging
logging.basicConfig(level=logging.INFO)


# Handler for the remove sponsor callback query
@router.callback_query(RemoveSponsor.filter())
async def remove_sponsor(callback_query: CallbackQuery, bot: Bot, callback_data: RemoveSponsor, db: MongoDbClient):
    await callback_query.answer('Remove')  # Send a response to the callback query

    # Delete the selected channel from the database
    await db.channels.delete_one({'channel_id': callback_data.channel_id})
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
    await bot.edit_message_text(chat_id=callback_query.from_user.id, text="Channels:",
                                reply_markup=markup.as_markup(), message_id=callback_query.message.message_id)
