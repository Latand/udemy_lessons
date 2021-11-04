from typing import Dict, Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.infrastructure.database.database_context import DatabaseContext
from tgbot.infrastructure.database.models.user import User
from tgbot.misc.constants import SESSION_POOL_KEY


class DatabaseMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        session_pool: sessionmaker = obj.bot.get(SESSION_POOL_KEY)
        session: AsyncSession = session_pool()
        data["user_db"] = DatabaseContext(session, query_model=User)
        data["session"] = session_pool()

    async def post_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        if session := data.get("session", None):
            session: AsyncSession
            await session.close()
