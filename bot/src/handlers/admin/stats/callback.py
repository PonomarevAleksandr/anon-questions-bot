from aiogram import Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks import AdminStats, AdminPanel
from src.utils.db import MongoDbClient

router = Router()


# Handler for displaying admin panel statistics
@router.callback_query(AdminStats.filter())
async def check_stats(callback_query: CallbackQuery, db: MongoDbClient, bot: Bot):
    # Count the number of users in the database
    users = await db.users.count({})

    # Answer the callback query with a message 'Statistics'
    await callback_query.answer('Statistics')

    # Create a keyboard with a 'Back' button
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text='Back', callback_data=AdminPanel().pack()))

    # Edit the message text to show the number of users with the keyboard
    await bot.edit_message_text(chat_id=callback_query.from_user.id, text=f'Number of users: {users}',
                                message_id=callback_query.message.message_id, reply_markup=keyboard.as_markup())
