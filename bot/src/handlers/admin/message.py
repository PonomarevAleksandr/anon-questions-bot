import logging
import time
from datetime import datetime
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, CallbackQuery, InlineKeyboardButton, InputMediaPhoto, InputMediaAnimation, \
    Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.callbacks import AdminStats, AdminUpload, AdminMailing, AdminChannels, AdminRefs, AdminAdv

router = Router()


# Admin-panel keyboard
@router.message(Command('admin'))
async def admin_panel(message: Message):
    # Check if the user ID matches the admin IDs
    if message.from_user.id == 686138890 or message.from_user.id == 1291860365:
        keyboard_admin = InlineKeyboardBuilder()

        # Add buttons to the keyboard for different admin actions
        keyboard_admin.row(
            InlineKeyboardButton(text='Statistics📊', callback_data=AdminStats().pack()),
            InlineKeyboardButton(text='Upload📝', callback_data=AdminUpload().pack())
        )
        keyboard_admin.row(
            InlineKeyboardButton(text='Mailing📩', callback_data=AdminMailing().pack()),
            InlineKeyboardButton(text='Channels🗣️', callback_data=AdminChannels().pack())
        )
        keyboard_admin.row(
            InlineKeyboardButton(text='Referrals🔗', callback_data=AdminRefs().pack()),
            InlineKeyboardButton(text='Advertisement Post📢', callback_data=AdminAdv().pack())
        )

        # Send the admin panel message with the keyboard
        await message.answer("Admin panel:", reply_markup=keyboard_admin.as_markup())
