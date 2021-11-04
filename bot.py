import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.storage import BaseStorage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config, Config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.misc.constants import SESSION_POOL_KEY, ENGINE_KEY

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(DatabaseMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)

    register_echo(dp)


class StorageFactory:
    """Создает хранилище в зависимости от значений параметров в конфиге"""

    def __init__(self, config: Config):
        self._config = config

    def create_storage(self) -> BaseStorage:
        if self._config.tg_bot.use_redis:
            return RedisStorage2()
        return MemoryStorage()


async def _close_resources(dp: Dispatcher):
    # закрываем сторедж и сессию бота
    await dp.storage.close()
    await dp.storage.wait_closed()
    await dp.bot.session.close()

    # закрываем все подключения к базе данных
    engine: AsyncEngine = dp.bot[ENGINE_KEY]
    await engine.dispose()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    # create aiogram components
    storage = StorageFactory(config=config).create_storage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    # create database
    engine = create_async_engine(
        config.db.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=100,
        max_overflow=200,
        future=True,
        echo=True
    )
    session_pool = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    bot[SESSION_POOL_KEY] = session_pool
    bot[ENGINE_KEY] = engine

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
