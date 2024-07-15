import logging
from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.callbacks import AdminChannels, AddSponsor, RemoveSponsor, SponsorList, ChannelSelect, AdminPanel, \
    ReferralSelect, AddReferral, AdminRefs, RemoveReferral
from src.utils.db import MongoDbClient
from src.utils.fsm_state import EditSponsorFSM, AddSponsorFSM
from src.utils.functions.admin.function import build_keyboard, edit_message, build_keyboard_referrals, \
    generate_random_string

router = Router()


# Handler for displaying the list of referrals
@router.callback_query(AdminRefs.filter())
async def referrals_list(callback_query: CallbackQuery, db: MongoDbClient, bot: Bot):
    # Fetch all referrals from the database
    referrals = await db.referrals.find({})

    # Create a list of referrals with their id, link, and clicks
    referrals_list = [{'id': referral.id, 'link': referral.link, 'clicks': referral.clicks} for referral in referrals]
    builder = InlineKeyboardBuilder()
    # Send a notification to the user
    await callback_query.answer('Referrals')
    # Add each referral to the inline keyboard
    for referral in referrals_list:
        builder.row(InlineKeyboardButton(text=referral['id'],
                                         callback_data=ReferralSelect(id=referral['id']).pack()))
    # Add buttons for adding a new referral and going back to the admin panel
    builder.row(InlineKeyboardButton(text='Add', callback_data=AddReferral().pack()))
    builder.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))
    # Edit the message to display the list of referrals
    await bot.edit_message_text(chat_id=callback_query.from_user.id, text="Referrals:",
                                message_id=callback_query.message.message_id, reply_markup=builder.as_markup())


# Handler for selecting a specific referral
@router.callback_query(ReferralSelect.filter())
async def referrals_select(callback_query: CallbackQuery, callback_data: ReferralSelect, bot: Bot, db: MongoDbClient):
    # Fetch the selected referral's information from the database
    info = await db.referrals.find_one({'id': str(callback_data.id)})
    # Send a notification to the user with the referral's id
    await callback_query.answer(info.id)
    # Build a keyboard for the selected referral
    keyboard = build_keyboard_referrals(str(callback_data.id))
    # Edit the message to display the referral's details
    await edit_message(bot, callback_query.from_user.id, callback_query.message.message_id,
                       f'ID : {info.id}\n\nLink : {info.link}\nClicks : {info.clicks}\n\n', keyboard)


# Handler for adding a new referral
@router.callback_query(AddReferral.filter())
async def referrals_add(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient):
    # Send a notification to the user
    await callback_query.answer('Add')
    # Generate a new random id for the referral
    new_id = await generate_random_string()
    # Insert the new referral into the database
    await db.referrals.insert_one({'id': new_id, 'link': f'https://t.me/anonfm_bot?start={new_id}'})
    # Fetch the new referral's information from the database
    info = await db.referrals.find_one({'id': str(new_id)})
    # Send a notification to the user with the new referral's id
    await callback_query.answer(info.id)
    # Build a keyboard for the new referral
    keyboard = build_keyboard_referrals(str(new_id))
    # Edit the message to display the new referral's details
    await edit_message(bot, callback_query.from_user.id, callback_query.message.message_id,
                       f'ID : {info.id}\n\nLink : {info.link}\nClicks : {info.clicks}\n\n', keyboard)


# Handler for removing a referral
@router.callback_query(RemoveReferral.filter())
async def remove_sponsor(callback_query: CallbackQuery, bot: Bot, callback_data: RemoveReferral, db: MongoDbClient):
    # Delete the selected referral from the database

    await db.referrals.delete_one({'id': callback_data.id})
    # Fetch all remaining referrals from the database
    referrals = await db.referrals.find({})
    # Create a list of remaining referrals with their id, link, and clicks
    referrals_list = [{'id': referral.id, 'link': referral.link, 'clicks': referral.clicks} for referral in referrals]
    builder = InlineKeyboardBuilder()
    # Send a notification to the user
    await callback_query.answer('Referrals')
    # Add each remaining referral to the inline keyboard
    for referral in referrals_list:
        builder.row(InlineKeyboardButton(text=referral['id'],
                                         callback_data=ReferralSelect(id=referral['id']).pack()))
    # Add buttons for adding a new referral and going back to the admin panel
    builder.row(InlineKeyboardButton(text='Add', callback_data=AddReferral().pack()))
    builder.row(InlineKeyboardButton(text='Back', callback_data=AdminRefs().pack()))
    # Edit the message to display the updated list of referrals
    await bot.edit_message_text(chat_id=callback_query.from_user.id, text="Referrals:",
                                message_id=callback_query.message.message_id, reply_markup=builder.as_markup())
