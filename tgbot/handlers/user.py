from typing import Optional

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.deep_linking import get_start_link

from tgbot.infrastructure.database.database_context import DatabaseContext
from tgbot.infrastructure.database.models.user import User


def _get_user_referrer_id(m: Message) -> Optional[int]:
    possible_id = m.get_args()
    if not possible_id:
        return None
    if not possible_id.isdigit():
        return None
    return int(possible_id)


async def user_start(message: Message, user_db: DatabaseContext[User]):
    await user_db.add(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.first_name,
        username=message.from_user.username,
        referrer_id=_get_user_referrer_id(message)
    )
    users_count = await user_db.count()
    ref_link = await get_start_link(message.from_user.id)
    await message.answer(
        "\n".join(
            [
                f'Привет, {message.from_user.full_name}!',
                f'Кол-во человек в базе: {users_count}'
                f'Ваша реферальная ссылка: {ref_link}'
            ])
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
