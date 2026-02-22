from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from infrastructure.database.models import Base
import os

class PostgresDatabase:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    async def initialize(self):
        """init con to db"""
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost/trackdb"
        )
        
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        
        self.async_session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        #Create Table
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        """close conn"""
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """get db session"""
        if not self.async_session_maker:
            await self.initialize()
        
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()