from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks import AdminAdv, AddAdv, AdvNav, AdvRemove, AdvEdit, AdvTextEdit, AdvMediaEdit
from src.utils.db import MongoDbClient
from src.utils.fsm_state import SendAdv, EditText, EditMedia
from src.utils.functions.admin.function import send_no_adv_message, send_media, create_keyboard

router = Router()


# Callback for checking advertisement posts
@router.callback_query(AdminAdv.filter())
async def admin_adv_initial(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient):
    await callback_query.answer('Advertisement')  # Send a response to the callback query
    adv_query = await db.adv.find_one_with_min_adv_id()  # Find the advertisement post with the minimum ID
    if not adv_query:
        await send_no_adv_message(bot,
                                  callback_query)  # If the post is not found
        return

    kwargs = {'caption': adv_query.caption} if adv_query.caption else {}  # If the post has a caption, add it to kwargs
    next_adv_query = await db.adv.find_one_with_next_adv_id(adv_query.adv_id)  # Find the next advertisement post
    builder = InlineKeyboardBuilder()  # Create a builder for the inline keyboard
    builder.row(InlineKeyboardButton(text='Edit Post', callback_data=AdvEdit(
        adv_id=int(adv_query.adv_id)).pack()))  # Add "Edit Post" button
    adv_quantity = await db.adv.count({})  # Count the number of advertisement posts
    if adv_quantity > 1:
        builder.add(InlineKeyboardButton(text='Next', callback_data=AdvNav(
            index=next_adv_query.adv_id).pack()))  # If there are more than one post, add "Next" button
    builder.row(InlineKeyboardButton(text='Add Post', callback_data=AddAdv().pack()))  # Add "Add Post" button
    builder.add(InlineKeyboardButton(text='Delete Post', callback_data=AdvRemove(
        adv_id=int(adv_query.adv_id)).pack()))  # Add "Delete Post" button
    await send_media(bot, callback_query, adv_query, builder,
                     **kwargs)  # Send the media with the advertisement post and keyboard


# Callback for adding an advertisement post
@router.callback_query(AddAdv.filter())
async def add_adv(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    await callback_query.answer('Add')  # Send a response to the callback query
    msg = await bot.send_message(chat_id=callback_query.from_user.id,
                                 text='Send the advertisement post')  # Ask the user to send the advertisement post
    await state.set_state(SendAdv.send_adv)  # Set the FSM state for sending the advertisement
    await state.update_data(main_message_id=callback_query.message.message_id,
                            message_id=msg.message_id)  # Update the FSM data


# Callback  for navigating through advertisement posts
@router.callback_query(AdvNav.filter())
async def admin_adv_navigation(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient, callback_data: AdvNav):
    await callback_query.answer('Advertisement')  # Send a response to the callback query
    current_adv_id = callback_data.index  # Get the current advertisement ID
    adv_query = await db.adv.find_one({'adv_id': int(current_adv_id)})  # Find the advertisement post by ID
    if not adv_query:
        await bot.send_message(callback_query.from_user.id,
                               text='Advertisement posts not found.')  # If the post is not found, send a message
        return

    kwargs = {'caption': adv_query.caption} if adv_query.caption else {}  # If the post has a caption, add it to kwargs
    builder = InlineKeyboardBuilder()  # Create a builder for the inline keyboard

    # Find the previous advertisement post
    prev_adv_query = await db.adv.find_one_with_prev_adv_id(current_adv_id)
    builder.row(InlineKeyboardButton(text='Edit Post', callback_data=AdvEdit(
        adv_id=int(adv_query.adv_id)).pack()))  # Add "Edit Post" button

    if prev_adv_query:
        builder.row(InlineKeyboardButton(text='Back', callback_data=AdvNav(
            index=prev_adv_query.adv_id).pack()))  # If the previous post is found, add "Back" button
    else:
        pass

    # Find the next advertisement post
    next_adv_query = await db.adv.find_one_with_next_adv_id(current_adv_id)
    if next_adv_query:
        builder.add(InlineKeyboardButton(text='Next', callback_data=AdvNav(
            index=next_adv_query.adv_id).pack()))  # If the next post is found, add "Next" button

    builder.row(InlineKeyboardButton(text='Add Post', callback_data=AddAdv().pack()))  # Add "Add Post" button
    builder.add(InlineKeyboardButton(text='Delete Post', callback_data=AdvRemove(
        adv_id=int(adv_query.adv_id)).pack()))  # Add "Delete Post" button

    await send_media(bot, callback_query, adv_query, builder,
                     **kwargs)  # Send the media with the advertisement post and keyboard


# Callback  for deleting an advertisement post
@router.callback_query(AdvRemove.filter())
async def admin_adv_remove(callback_query: CallbackQuery, bot: Bot, db: MongoDbClient, callback_data: AdvRemove):
    await callback_query.answer('Delete')  # Send a response to the callback query
    await db.adv.delete_one({'adv_id': int(callback_data.adv_id)})  # Delete the advertisement post from the database
    adv_query = await db.adv.find_one_with_min_adv_id()  # Find the advertisement post with the minimum ID
    if not adv_query:
        await send_no_adv_message(bot,
                                  callback_query)  # If the post is not found, send a message indicating no advertisements
        return

    kwargs = {'caption': adv_query.caption} if adv_query.caption else {}  # If the post has a caption, add it to kwargs
    await bot.delete_message(chat_id=callback_query.from_user.id,
                             message_id=callback_query.message.message_id)  # Delete the message with the advertisement post
    next_adv_query = await db.adv.find_one_with_next_adv_id(adv_query.adv_id)  # Find the next advertisement post
    adv_quantity = await db.adv.count({})  # Count the number of advertisement posts
    builder = create_keyboard(adv_query, next_adv_query,
                              adv_quantity)  # Create the keyboard for navigating through advertisement posts
    await send_media(bot, callback_query, adv_query, builder,
                     **kwargs)  # Send the media with the advertisement post and keyboard


# Callback for choosing to edit an advertisement post
@router.callback_query(AdvEdit.filter())
async def adv_edit_choose(callback_query: CallbackQuery, callback_data: AdvEdit, bot: Bot):
    await callback_query.answer('Edit')  # Send a response to the callback query
    adv_id = int(callback_data.adv_id)  # Get the advertisement post ID
    keyboard = InlineKeyboardBuilder()  # Create a builder for the inline keyboard
    keyboard.row(InlineKeyboardButton(text='Edit Text',
                                      callback_data=AdvTextEdit(adv_id=adv_id).pack()))  # Add "Edit Text" button
    keyboard.row(InlineKeyboardButton(text='Edit Media',
                                      callback_data=AdvMediaEdit(adv_id=adv_id).pack()))  # Add "Edit Media" button
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=AdminAdv().pack()))  # Add "Back" button

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard.as_markup()  # Update the message's keyboard
    )


# Callback  for starting to edit the text of an advertisement post
@router.callback_query(AdvTextEdit.filter())
async def adv_text_edit_start(callback_query: CallbackQuery, callback_data: AdvTextEdit, bot: Bot, state: FSMContext):
    await callback_query.answer('Text')  # Send a response to the callback query
    adv_id = int(callback_data.adv_id)  # Get the advertisement post ID
    msg = await bot.send_message(
        chat_id=callback_query.from_user.id,
        text='Enter the new text (HTML tags are supported):'
    )  # Ask the user to enter the new text
    await state.set_state(EditText.edit_text)  # Set the FSM state for editing the text
    await state.update_data(adv_id=adv_id, message_id=msg.message_id,
                            main_message_id=callback_query.message.message_id)  # Send data to state


# Callback for starting to edit the media of an advertisement post

@router.callback_query(AdvMediaEdit.filter())
async def adv_media_edit_start(callback_query: CallbackQuery, callback_data: AdvMediaEdit, bot: Bot, state: FSMContext):
    await callback_query.answer('Media')  # Send a response to the callback query

    adv_id = int(callback_data.adv_id)  # Get the advertisement post ID
    msg = await bot.send_message(
        chat_id=callback_query.from_user.id,
        text='Send new media file:')  # Ask the user to send the new media
    await state.set_state(EditMedia.edit_media)  # Set the FSM state for editing the media
    await state.update_data(adv_id=adv_id, message_id=msg.message_id,
                            main_message_id=callback_query.message.message_id)  # Send data to state
