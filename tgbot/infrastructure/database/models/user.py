from sqlalchemy import Column, VARCHAR, BIGINT
from sqlalchemy.sql import expression

from tgbot.infrastructure.database.models.base import TimedBaseModel


class User(TimedBaseModel):
    telegram_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    first_name = Column(VARCHAR(200), nullable=False)
    # last_name и username могут быть NULL, так как это позволяет телеграмм
    last_name = Column(VARCHAR(200), server_default=expression.null(), nullable=True)
    username = Column(VARCHAR(200), server_default=expression.null(), nullable=True)
