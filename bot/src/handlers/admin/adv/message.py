import time
from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.utils.db import MongoDbClient
from src.utils.fsm_state import SendAdv, EditMedia, EditText
from src.utils.functions.admin.function import send_no_adv_message, \
    create_keyboard, handle_media, send_adv_message, update_adv_data

router = Router()


# Handler for sending advertisements
@router.message(SendAdv.send_adv)
async def send_adv(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    # Get data from the state
    data = await state.get_data()
    # Delete the message from the user
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=int(data.get('message_id')))

    # Handle media content in the message
    content, content_type = await handle_media(message)
    # Find the document with the maximum advertisement ID
    max_adv_document = await db.adv.find_one_with_max_adv_id()
    max_adv_id = max_adv_document.adv_id if max_adv_document else 0
    # Create a dictionary with the message data
    message_data = {
        'date': time.time(),
        'content': content,
        'content_type': content_type,
        'caption': message.caption,
        'adv_id': int(max_adv_id) + 1
    }

    # Insert the message data into the database
    await db.adv.insert_one(message_data)
    # Clear the state
    await state.clear()
    # Find the document with the minimum advertisement ID
    adv_query = await db.adv.find_one_with_min_adv_id()
    if not adv_query:
        await bot.send_message(message.from_user.id, text='Adv posts not found')
        return

    # Create a dictionary with the caption if it exists
    kwargs = {'caption': adv_query.caption} if adv_query.caption else {}
    # Find the document with the next advertisement ID
    next_adv_query = await db.adv.find_one_with_next_adv_id(adv_query.adv_id)
    # Count the number of advertisements in the database
    adv_quantity = await db.adv.count({})
    if adv_quantity == 1:
        await bot.delete_message(chat_id=message.from_user.id, message_id=int(data.get('main_message_id')))
    # Create a keyboard for the advertisement
    builder = create_keyboard(adv_query, next_adv_query, adv_quantity)
    # Send the media message with the advertisement
    await send_adv_message(bot, message, adv_query, builder, data.get('main_message_id'), **kwargs)


# Handler for editing media in advertisements
@router.message(EditMedia.edit_media)
async def edit_media_adv(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    # Delete the message from the user
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=int(data.get('message_id')))

    # Handle media content in the message
    content, content_type = await handle_media(message)
    # Create a dictionary with the message data
    message_data = {'content': content, 'content_type': content_type}
    # Update the advertisement in the database
    await update_adv_data(db, data.get('adv_id'), message_data)

    # Find the advertisement in the database
    adv_query = await db.adv.find_one(({'adv_id': int(data.get('adv_id'))}))
    if not adv_query:
        await send_no_adv_message(bot, message)
        return

    # Create a dictionary with the caption if it exists
    kwargs = {'caption': adv_query.caption} if adv_query.caption else {}
    # Find the document with the next advertisement ID
    next_adv_query = await db.adv.find_one_with_next_adv_id(adv_query.adv_id)
    # Count the number of advertisements in the database
    adv_quantity = await db.adv.count({})
    # Create a keyboard for the advertisement
    builder = create_keyboard(adv_query, next_adv_query, adv_quantity)
    # Send the media message with the advertisement
    await send_adv_message(bot, message, adv_query, builder, data.get('main_message_id'), **kwargs)


# Handler for editing text in advertisements
@router.message(EditText.edit_text)
async def edit_text_adv(message: Message, bot: Bot, state: FSMContext, db: MongoDbClient):
    # Delete the message from the user
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=int(data.get('message_id')))

    # Update the advertisement in the database with the new text
    await update_adv_data(db, data.get('adv_id'), {'caption': message.text})

    # Find the advertisement in the database
    adv_query = await db.adv.find_one(({'adv_id': int(data.get('adv_id'))}))
    if not adv_query:
        await send_no_adv_message(bot, message)
        return

    # Create a dictionary with the caption if it exists
    kwargs = {'caption': adv_query.caption} if adv_query.caption else {}
    # Find the document with the next advertisement ID
    next_adv_query = await db.adv.find_one_with_next_adv_id(adv_query.adv_id)
    # Count the number of advertisements in the database
    adv_quantity = await db.adv.count({})
    # Create a keyboard for the advertisement
    builder = create_keyboard(adv_query, next_adv_query, adv_quantity)
    # Send the media message with the advertisement
    await send_adv_message(bot, message, adv_query, builder, data.get('main_message_id'), **kwargs)
