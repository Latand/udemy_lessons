from typing import Type, Generic, Union, TypeVar, Optional, cast, List, Any, \
    Sequence, Callable

from sqlalchemy import delete, exists, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.orm import sessionmaker, Session  # noqa
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.elements import BinaryExpression

ASTERISK = "*"

SQLAlchemyModel = TypeVar("SQLAlchemyModel")
ExpressionType = Union[BinaryExpression, ClauseElement, bool]


class Database(Generic[SQLAlchemyModel]):
    def __init__(
            self,
            session_or_pool: Union[sessionmaker, AsyncSession],
            *,
            query_model: Type[SQLAlchemyModel],
    ) -> None:
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool
        self.model = query_model

    async def add(self, **values: Any) -> SQLAlchemyModel:
        async with self._session.begin():
            insert_stmt = insert(self.model).values(
                **values
            ).on_conflict_do_nothing().returning(ASTERISK)
            result = await self._session.execute(insert_stmt)
        return result.scalars().first()

    async def add_many(self, *models: SQLAlchemyModel) -> None:
        async with self._session.begin():
            bulk_save_func = make_proxy_bulk_save_func(instances=models)
            await self._session.run_sync(bulk_save_func)

    async def get_all(self, *clauses: ExpressionType) -> List[SQLAlchemyModel]:
        async with self._session.begin():
            statement = select(self.model).where(*clauses)
            result: AsyncResult = await self._session.execute(statement)
            scalars = result.scalars().all()
        return cast(List[SQLAlchemyModel], scalars)

    async def get_one(self, *clauses: ExpressionType) -> Optional[SQLAlchemyModel]:
        async with self._session.begin():
            statement = select(self.model).where(*clauses)
            result: AsyncResult = await self._session.execute(statement)
            first_scalar_result = result.scalars().first()
        return first_scalar_result

    async def update(self, *clauses: ExpressionType, **values: Any) -> None:
        async with self._session.begin():
            statement = update(self.model).where(*clauses).values(**values)
            await self._session.execute(statement)

    async def exists(self, *clauses: ExpressionType) -> bool:
        async with self._session.begin():
            statement = exists(select(self.model).where(*clauses)).select()
            result = (await self._session.execute(statement)).scalar()
        return cast(bool, result)

    async def delete(self, *clauses: ExpressionType) -> List[SQLAlchemyModel]:
        async with self._session.begin():
            statement = delete(self.model).where(*clauses).returning(ASTERISK)
            result = (await self._session.execute(statement)).scalars().all()
        return cast(List[SQLAlchemyModel], result)

    async def count(self, *clauses: ExpressionType) -> int:
        async with self._session.begin():
            statement = select(func.count(ASTERISK)).where(*clauses)
            result: AsyncResult = await self._session.execute(statement)
        return cast(int, result.scalar())


def make_proxy_bulk_save_func(
        instances: Sequence[Any],
        return_defaults: bool = False,
        update_changed_only: bool = True,
        preserve_order: bool = True,
) -> Callable[[Session], None]:
    def _proxy(session: Session) -> None:
        return session.bulk_save_objects(
            instances,
            return_defaults=return_defaults,
            update_changed_only=update_changed_only,
            preserve_order=preserve_order,
        )  # type: ignore

    return _proxy
