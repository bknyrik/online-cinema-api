from typing import AsyncGenerator

from src.database.config import SessionLocal


async def get_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session
