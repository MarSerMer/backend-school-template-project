from typing import TYPE_CHECKING, Any, TypeVar, Union

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.store.database.sqlalchemy_base import BaseModel

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        self._db = BaseModel()
        db_data = self.app.config.database
        database_url = f"postgresql+asyncpg://{db_data.user}:{db_data.password}@{db_data.host}/{db_data.database}"
        self.engine = create_async_engine(
            database_url,
            echo=True
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.engine:
            await self.engine.dispose()

    async def select_from_database(self, query):
        async with self.session() as session:
            return await session.execute(query)

    async def add_to_database(self, obj: TypeVar | list[TypeVar]):
        async with self.session() as session:
            if isinstance(obj, list):
                session.add_all(obj)
            else:
                session.add(obj)
            await session.commit()

    async def delete_from_database(self, query):
        async with self.session() as session:
            delete_it = await self.select_from_database(query)
            await session.delete(delete_it)
            await session.commit()
