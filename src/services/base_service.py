from abc import ABCMeta

from sqlalchemy.ext.asyncio import AsyncSession
from src.config import Config


class BaseService(metaclass=ABCMeta):

    def __init__(
        self,
        session: AsyncSession,
        config: Config,
    ) -> None:

        self.session = session
        self.config = config
