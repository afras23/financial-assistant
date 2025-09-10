import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///./expenses.db")

engine = create_async_engine(DB_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def init_models():
    # Alembic manages schema in production; for tests we create tables if sqlite
    if DB_URL.startswith("sqlite"):
        from . import models  # noqa
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        # Light check to ensure DB reachable
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
