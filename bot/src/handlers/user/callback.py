from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks import Reply, GetLink, SendAgain, Start
from src.utils.db import MongoDbClient
from src.utils.fsm_state import SendMessage
from src.utils.functions.user.functions import check_all_subs, not_subscribe, start_with_referer, start_without_referer, \
    plus_sub, adv_show

router = Router()


# Reply start FSM
@router.callback_query(Reply.filter())
async def reply_callback(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient, state: FSMContext,
                         callback_data=Reply):
    # Check if the user is subscribed to all sponsor channels
    channels = await db.channels.find({})
    channels_list = [{'channel_id': channel.channel_id, 'url': channel.url, 'name': channel.name} for channel in
                     channels]
    all_subscribed = await check_all_subs(bot, callback_query.from_user.id, channels_list)
    if all_subscribed:
        # If subscribed, increment the subscription count
        await plus_sub(channels_list, db, callback_query.from_user.id)

        # Answer the callback query with a message 'Reply'
        await callback_query.answer('Reply')
        # Delete the original message
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        # Send a new message asking the user to enter their reply
        mes = await bot.send_message(chat_id=callback_query.from_user.id, text='Enter your message:')
        # Set the FSM state to SendMessage.send_message
        await state.set_state(SendMessage.send_message)
        # Update the FSM context with relevant data
        await state.update_data(referer=callback_data.referer, message_id=mes.message_id, action=callback_data.action,
                                reply_message=callback_data.reply_message, sender=callback_data.sender)
    else:
        # If not subscribed, prompt the user to subscribe
        callback = Reply(sender=int(callback_data.sender), action='reply',
                         referer=int(callback_data.referer),
                         reply_message=callback_data.reply_message).pack()
        await not_subscribe(bot, callback_query.from_user.id, channels_list,
                            callback, int(callback_query.message.message_id))


# Link generation
@router.callback_query(GetLink.filter())
async def get_link(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient, callback_data: GetLink):
    # Check if the user is subscribed to all sponsor channels
    channels = await db.channels.find({})
    channels_list = [{'channel_id': channel.channel_id, 'url': channel.url, 'name': channel.name} for channel in
                     channels]
    all_subscribed = await check_all_subs(bot, callback_query.from_user.id, channels_list)
    if all_subscribed:
        # If subscribed, increment the subscription count
        await plus_sub(channels_list, db, callback_query.from_user.id)
        me = await bot.get_me()
        await callback_query.answer('My link')
        referer = callback_data.referer

        if callback_data.check_my:
            # If the user is checking their own link
            await bot.edit_message_caption(chat_id=callback_query.from_user.id,
                                           message_id=callback_query.message.message_id,
                                           caption=f"🔗 Here is your personal link:\n\n"
                                                   f"🔗 <code>https://t.me/{me.username}"
                                                   f"?start={callback_query.from_user.id}"
                                                   f"</code>\n\n"
                                                   f"Share it and receive anonymous messages")  # No keyboard
        else:
            keyboard_sender = InlineKeyboardBuilder()
            keyboard_sender.row(InlineKeyboardButton(text='Send again',
                                                     callback_data=SendAgain(referer=int(referer),
                                                                             action='send').pack()))
            await bot.edit_message_caption(chat_id=callback_query.from_user.id,
                                           message_id=callback_query.message.message_id,
                                           caption=f"🔗 Here is your personal link:\n\n"
                                                   f"🔗 <code>https://t.me/{me.username}"
                                                   f"?start={callback_query.from_user.id}"
                                                   f"</code>\n\n"
                                                   f"Share it and receive anonymous messages",
                                           reply_markup=keyboard_sender.as_markup())
    else:
        # If not subscribed, prompt the user to subscribe
        callback = GetLink(referer=int(callback_data.referer), check_my=callback_data.check_my).pack()
        await not_subscribe(bot, callback_query.from_user.id, channels_list,
                            callback, int(callback_query.message.message_id))
    await adv_show(callback_query.from_user.id, bot, db)


# Send one more question FSM start
@router.callback_query(SendAgain.filter())
async def send_again(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient, callback_data: SendAgain,
                     state: FSMContext):
    # Check if the user is subscribed to all sponsor channels
    channels = await db.channels.find({})
    channels_list = [{'channel_id': channel.channel_id, 'url': channel.url, 'name': channel.name} for channel in
                     channels]
    all_subscribed = await check_all_subs(bot, callback_query.from_user.id, channels_list)
    if all_subscribed:
        # If subscribed, increment the subscription count
        await plus_sub(channels_list, db, callback_query.from_user.id)
        reply_target = callback_data.referer
        await callback_query.answer('Send again')
        action = callback_data.action
        # Delete the original message
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

        # Send a new message asking the user to enter their reply
        mes = await bot.send_message(chat_id=callback_query.from_user.id, text='Enter your message:')
        # Set the FSM state to SendMessage.send_message
        await state.set_state(SendMessage.send_message)
        # Update the FSM context with relevant data
        await state.update_data(referer=reply_target, message_id=mes.message_id, action=action)
    else:
        # If not subscribed, prompt the user to subscribe
        callback = SendAgain(referer=int(callback_data.referer), action='send').pack()
        await not_subscribe(bot, callback_query.from_user.id, channels_list,
                            callback, int(callback_query.message.message_id))


# Start callback
@router.callback_query(Start.filter())
async def reply_callback(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient, state: FSMContext,
                         callback_data: Start):
    # Delete the original message
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    # Check if the user is subscribed to all sponsor channels
    channels = await db.channels.find({})
    channels_list = [{'channel_id': channel.channel_id, 'url': channel.url, 'name': channel.name} for channel in
                     channels]
    all_subscribed = await check_all_subs(bot, callback_query.from_user.id, channels_list)
    if all_subscribed:
        # If subscribed, increment the subscription count
        await plus_sub(channels_list, db, callback_query.from_user.id)
        if callback_data.message.startswith('/start ') and len(callback_data.message.split('/start ')[1]) > 0:
            # If the user started from a link
            await start_with_referer(callback_query, bot, state, callback_data.message)
        else:
            # If the user started without a link
            await start_without_referer(callback_query, bot, state)
    else:
        # If not subscribed, prompt the user to subscribe
        callback = Start(message=callback_data.message).pack()
        await not_subscribe(bot, callback_query.from_user.id, channels_list,
                            callback, int(callback_query.message.message_id))
    await adv_show(callback_query.from_user.id, bot, db)
