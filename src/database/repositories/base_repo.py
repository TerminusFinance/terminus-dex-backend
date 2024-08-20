from abc import ABCMeta

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(metaclass=ABCMeta):

    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session
