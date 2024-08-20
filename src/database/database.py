from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.config import Config, ConfigManager
from src.utils.singleton import SingletonMeta


class DatabaseSessionManager(metaclass=SingletonMeta):
    engine: AsyncEngine
    sessionmaker: async_sessionmaker

    def __init__(
        self,
        config: Config | None = None,
    ) -> None:

        if not config:
            config = ConfigManager().get_config()

        self.engine = create_async_engine(
            create_postgres_connection_url(**config.database.as_dict())
        )
        self.sessionmaker = async_sessionmaker(
            self.engine, expire_on_commit=False, autoflush=False
        )

    # async def init_database(self) -> None:
    #     url = ConfigManager().database.url_sync

    #     if not database_exists(url):
    #         create_database(url)

    #     async with self.engine.begin() as connection:
    #         await connection.run_sync(database_models.Base.metadata.create_all)

    def create_session(self) -> AsyncSession:
        return self.sessionmaker()


def create_postgres_connection_url(
    host: str,
    port: int,
    user: str,
    password: str,
    db_name: str,
    is_sync: bool = False,
    use_localhost: bool = False,
) -> str:

    host = "localhost" if use_localhost else host

    if is_sync:
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
