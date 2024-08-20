from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import Config
from src.database.database import DatabaseSessionManager

from .config import get_config


async def get_session(
    config: Annotated[Config, Depends(get_config)]
) -> AsyncIterator[AsyncSession]:

    session_manager = DatabaseSessionManager(config=config)
    session_maker = session_manager.sessionmaker

    if session_maker is None:
        raise Exception("DatabaseSessionManager is not initialized")

    async with session_maker() as session:
        yield session
