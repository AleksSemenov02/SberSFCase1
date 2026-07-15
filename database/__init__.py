from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from settings import App

engine = create_async_engine(App.database_url)
Session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with Session() as session:
        yield session
