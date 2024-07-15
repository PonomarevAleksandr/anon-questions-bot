import logging
import random
import secrets
import string

from aiogram.types import InlineKeyboardButton, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.callbacks import AddSponsor, SponsorList, RemoveSponsor, ReferralList, RemoveReferral, AdminRefs, AdvEdit, \
    AdminPanel, AdvNav, AddAdv, AdvRemove
from src.utils.photo import no_photo


# Function to update channel data in the database
async def update_channel_data(db, filter, update):
    try:
        # Attempt to update the channel data
        result = await db.channels.update_one(filter, update)
        if result.modified_count > 0:
            logging.info('Document successfully updated.')
        else:
            logging.info('Document for update not found.')
    except Exception as e:
        logging.error(f'Error updating document: {e}')


# Function to build a keyboard for channel management
def build_keyboard(channel_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Remove Sponsor', callback_data=RemoveSponsor(channel_id=channel_id).pack()))
    keyboard.row(
        InlineKeyboardButton(text='Edit Name', callback_data=AddSponsor(edit='name', channel_id=channel_id).pack()))
    keyboard.row(
        InlineKeyboardButton(text='Edit ID', callback_data=AddSponsor(edit='id', channel_id=channel_id).pack()))
    keyboard.row(
        InlineKeyboardButton(text='Edit URL', callback_data=AddSponsor(edit='url', channel_id=channel_id).pack()))
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=SponsorList().pack()))
    return keyboard


# Function to edit a message
async def edit_message(bot, chat_id, message_id, text, keyboard):
    await bot.edit_message_text(chat_id=chat_id, text=text, message_id=message_id, reply_markup=keyboard.as_markup())


# Function to generate a random string
async def generate_random_string():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(16))
    return random_string


# Function to build a keyboard for referral management
def build_keyboard_referrals(ref_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='Remove', callback_data=RemoveReferral(id=ref_id).pack()))
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=AdminRefs().pack()))
    return keyboard


# Function to create a keyboard for advertisement management
def create_keyboard(adv_query, next_adv_query, adv_quantity):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Edit Post', callback_data=AdvEdit(adv_id=int(adv_query.adv_id)).pack()))
    if int(adv_quantity) >= 2:
        builder.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    if int(adv_quantity) > 1:
        builder.add(InlineKeyboardButton(text='Next', callback_data=AdvNav(index=next_adv_query.adv_id).pack()))
    builder.row(InlineKeyboardButton(text='Add Post', callback_data=AddAdv().pack()))
    builder.add(InlineKeyboardButton(text='Remove Post', callback_data=AdvRemove(adv_id=int(adv_query.adv_id)).pack()))
    return builder


# Function to send media content
async def send_media(bot, callback_query, adv_query, builder, **kwargs):
    try:
        if adv_query.content_type == 'photo':
            await bot.edit_message_media(chat_id=callback_query.from_user.id,
                                         media=InputMediaPhoto(media=adv_query.content, **kwargs, parse_mode='html'),
                                         message_id=callback_query.message.message_id, reply_markup=builder.as_markup())
        elif adv_query.content_type == 'video':
            await bot.edit_message_media(chat_id=callback_query.from_user.id,
                                         media=InputMediaVideo(media=adv_query.content, **kwargs, parse_mode='html'),
                                         message_id=callback_query.message.message_id, reply_markup=builder.as_markup())
        elif adv_query.content_type == 'document':
            await bot.edit_message_media(chat_id=callback_query.from_user.id,
                                         media=InputMediaDocument(media=adv_query.content, **kwargs, parse_mode='html'),
                                         message_id=callback_query.message.message_id, reply_markup=builder.as_markup())
        elif adv_query.content_type == 'text':
            await bot.edit_message_media(chat_id=callback_query.from_user.id,
                                         media=InputMediaPhoto(media=no_photo, caption=adv_query.content,
                                                               parse_mode='html'),
                                         message_id=callback_query.message.message_id, reply_markup=builder.as_markup())
    except:
        if adv_query.content_type == 'photo':
            await bot.send_photo(callback_query.from_user.id, photo=adv_query.content, reply_markup=builder.as_markup(),
                                 **kwargs, parse_mode='html')
        elif adv_query.content_type == 'video':
            await bot.send_video(callback_query.from_user.id, video=adv_query.content, reply_markup=builder.as_markup(),
                                 **kwargs, parse_mode='html')
        elif adv_query.content_type == 'document':
            await bot.send_document(callback_query.from_user.id, document=adv_query.content,
                                    reply_markup=builder.as_markup(), **kwargs, parse_mode='html')
        elif adv_query.content_type == 'text':
            await bot.send_message(callback_query.from_user.id, text=adv_query.content,
                                   reply_markup=builder.as_markup(),
                                   parse_mode='html')


# Function to send a message when no advertisements are found
async def send_no_adv_message(bot, callback_query):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Add Post', callback_data=AddAdv().pack()))
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text='No advertisement posts found.',
                           reply_markup=keyboard.as_markup())


# Function to send media message
async def send_media_message(bot, message, adv_query, builder, message_id, **kwargs):
    try:
        if adv_query.content_type == 'photo':
            await bot.edit_message_media(chat_id=message.from_user.id,
                                         media=InputMediaPhoto(media=adv_query.content, **kwargs, parse_mode='html'),
                                         message_id=message_id, reply_markup=builder.as_markup())
        elif adv_query.content_type == 'video':
            await bot.edit_message_media(chat_id=message.from_user.id,
                                         media=InputMediaVideo(media=adv_query.content, **kwargs, parse_mode='html'),
                                         message_id=message_id, reply_markup=builder.as_markup())
        elif adv_query.content_type == 'document':
            await bot.edit_message_media(chat_id=message.from_user.id,
                                         media=InputMediaDocument(media=adv_query.content, **kwargs, parse_mode='html'),
                                         message_id=message_id, reply_markup=builder.as_markup())
        elif adv_query.content_type == 'text':
            await bot.edit_message_media(chat_id=message.from_user.id,
                                         media=InputMediaPhoto(media=no_photo, caption=adv_query.content,
                                                               parse_mode='html'),
                                         message_id=message_id, reply_markup=builder.as_markup())
    except:
        if adv_query.content_type == 'photo':
            await bot.send_photo(message.from_user.id, photo=adv_query.content, reply_markup=builder.as_markup(),
                                 **kwargs, parse_mode='html')
        elif adv_query.content_type == 'video':
            await bot.send_video(message.from_user.id, video=adv_query.content, reply_markup=builder.as_markup(),
                                 **kwargs, parse_mode='html')
        elif adv_query.content_type == 'document':
            await bot.send_document(message.from_user.id, document=adv_query.content,
                                    reply_markup=builder.as_markup(), **kwargs, parse_mode='html')
        elif adv_query.content_type == 'text':
            await bot.send_message(message.from_user.id, text=adv_query.content,
                                   reply_markup=builder.as_markup(),
                                   parse_mode='html')


# Function to handle media content in the message
async def handle_media(message):
    content = None
    content_type = None
    # Check the type of content in the message and set the content and content_type accordingly
    if message.photo:
        content = message.photo[-1].file_id
        content_type = 'photo'
    elif message.video:
        content = message.video.file_id
        content_type = 'video'
    elif message.document:
        content = message.document.file_id
        content_type = 'document'
    elif message.text:
        content = message.text
        content_type = 'text'
    return content, content_type


# Function to update advertisement data in the database
async def update_adv_data(db, adv_id, data):
    await db.adv.update_one({'adv_id': int(adv_id)}, data)


# Function to send advertisement message
async def send_adv_message(bot, message, adv_query, builder, main_message_id, **kwargs):
    await send_media_message(bot, message, adv_query, builder, message_id=int(main_message_id), **kwargs)
