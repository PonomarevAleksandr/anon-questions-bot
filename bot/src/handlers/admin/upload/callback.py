import os
from aiogram import Bot, Router
from aiogram.types import CallbackQuery, FSInputFile
from src.callbacks import AdminUpload
from src.utils.db import MongoDbClient

router = Router()


# Admin-panel Stats
@router.callback_query(AdminUpload.filter())
async def upload_users(callback_query: CallbackQuery, db: MongoDbClient, bot: Bot):
    await callback_query.answer('Upload')  # Send a response to the callback query

    # Fetch users from the database with a limit of 10 billion
    users = await db.users.find({}, count=10000000000)
    txt = ''

    # Iterate over each user and append their ID to the text string
    for user in users:
        txt += f'{user.id}\n'

    # Write the user IDs to a file named 'users.txt'
    with open('users.txt', 'w') as f:
        f.write(txt)

    # Send the 'users.txt' file to the user who initiated the callback query
    await bot.send_document(chat_id=callback_query.from_user.id, document=FSInputFile('users.txt'))

    # Remove the 'users.txt' file after sending it
    os.remove('users.txt')
