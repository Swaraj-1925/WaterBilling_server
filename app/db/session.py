from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import  create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.constant import DB_URL
from utils.logger import logger

engine = create_async_engine(DB_URL)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
async def get_session()->AsyncGenerator[AsyncSession, None]:
    async  with SessionLocal() as session:
        yield session
async def create_db_and_tables():
    try:
        async with engine.begin() as conn:
            #await conn.run_sync(SQLModel.metadata.drop_all)
            #logger.info("Drop all tables")
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info(f"DB created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to the database: {e}")
        raise


