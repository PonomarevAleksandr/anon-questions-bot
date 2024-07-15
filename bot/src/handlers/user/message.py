from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.utils.db import MongoDbClient
from src.utils.fsm_state import SendMessage
from src.utils.functions.user.functions import (send_message_with_referer, adv_show, show_advert, handle_start,
                                                handle_subscription_check)

router = Router()


# Handle the /start command
@router.message(Command('start'))
async def start(message: Message, bot: Bot, db: MongoDbClient, state: FSMContext):
    # Split the message text by spaces
    split_message = message.text.split(' ')
    # Find the user in the database
    user = await db.users.find_one({'id': message.from_user.id})
    if user.first_start:
        # If this is the user's first start, update the database
        await db.users.update_one({'id': message.from_user.id}, {'first_start': False})
        await handle_start(message, bot, db, state, split_message)
    else:
        await handle_subscription_check(bot, message, db, state, split_message)
    # Show advertisement
    await show_advert(message.from_user.id)
    await adv_show(message.from_user.id, bot, db)


# Handle sending and replying to messages
@router.message(SendMessage.send_message)
async def send_message(message: Message, bot: Bot, db: MongoDbClient, state: FSMContext):
    # Get the FSM context data
    data = await state.get_data()
    if data.get('referer'):
        # If there is a referer, send the message with referer
        await send_message_with_referer(
            message, bot, state, data, int(data.get('referer')),
            int(data.get('sender')) if data.get('sender') else None
        )
    else:
        # If there is no referer, send an error message
        await message.answer("❗️ Unable to send message, referer is missing.")
    # Show advertisement
    await show_advert(message.from_user.id)
    await adv_show(message.from_user.id, bot, db)
    # Clear the FSM state
    await state.clear()
