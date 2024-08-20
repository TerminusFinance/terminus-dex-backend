# === === === === === === ===

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api.test.controller import test_router
from src.api.v1.controller import api_v1_router
from src.blockchains.ton.clients.client_manager import TonClientManager
from src.config import ConfigManager
from src.database.database import DatabaseSessionManager
from src.server.middlewares import auth_middleware
from src.utils.logging import init_logger

from .background_tasks.update_pools import update_pools_interval
from .init_tasks.add_default_assets import add_default_assets

# === === === === === === ===


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_logger()

    config = ConfigManager().get_config()
    ton_client = TonClientManager(config=config).get_ton_client()
    sessionmaker = DatabaseSessionManager(config=config).sessionmaker

    # === === === === === === ===

    loop = asyncio.get_event_loop()

    loop.create_task(add_default_assets(sessionmaker=sessionmaker))

    loop.create_task(
        update_pools_interval(
            interval=5 * 60,
            sessionmaker=sessionmaker,
            config=config,
            ton_client=ton_client,
        )
    )

    # === === === === === === ===

    yield


# === === === === === === ===


def register_middlewares(app: FastAPI) -> None:

    app.middleware("http")(auth_middleware)


# === === === === === === ===


def create_server() -> FastAPI:

    config = ConfigManager().get_config()

    core_app = FastAPI(
        debug=config.debug,
        title=config.app.name,
        version=config.app.version,
        root_path="/api",
        lifespan=lifespan,
    )

    register_middlewares(app=core_app)

    core_app.include_router(api_v1_router, prefix="/v1")
    core_app.include_router(test_router, prefix="/test")

    return core_app


# === === === === === === ===
