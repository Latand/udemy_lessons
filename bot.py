import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.storage import BaseStorage
from glQiwiApi import QiwiWrapper

from tgbot.config import load_config, Config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.echo import register_echo
from tgbot.handlers.pay_for_item import register_pay_for_item
from tgbot.handlers.user import register_user
from tgbot.middlewares.dependencies import TransferDependencyMiddleware
from tgbot.misc.constants import QIWI_CLIENT_KEY

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(TransferDependencyMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_pay_for_item(dp)
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

    # закрываем сессию киви кошелька
    qiwi_client: QiwiWrapper = dp.bot[QIWI_CLIENT_KEY]
    await qiwi_client.close()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = StorageFactory(config=config).create_storage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    # Киви клиент
    qiwi_client = QiwiWrapper(secret_p2p=config.qiwi.secret_p2p_token)

    bot['config'] = config
    bot[QIWI_CLIENT_KEY] = qiwi_client

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await _close_resources(dp)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
