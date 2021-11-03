from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.infrastructure.database.database import Database
from tgbot.infrastructure.database.models.user import User


async def user_start(message: Message, user_db: Database[User]):
    await user_db.add(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.first_name,
        username=message.from_user.username
    )
    users_count = await user_db.count()
    await message.answer(
        "\n".join(
            [
                f'Привет, {message.from_user.full_name}!',
                f'Ты был занесен в базу',
                f'В базе <b>{users_count}</b> пользователей',
            ])
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
