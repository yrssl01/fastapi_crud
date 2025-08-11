from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
new_async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_async_session() as session:
        yield session


class Base(DeclarativeBase, AsyncAttrs):
    pass
