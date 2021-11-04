from typing import Dict, Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from glQiwiApi import QiwiWrapper

from tgbot.misc.constants import QIWI_CLIENT_KEY


class TransferDependencyMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj: TelegramObject, data: Dict[Any, Any], *args: Any):
        qiwi_client: QiwiWrapper = obj.bot['qiwi_client']
        data[QIWI_CLIENT_KEY] = qiwi_client
