from typing import Annotated

from fastapi import Depends
from src.blockchains.ton.clients import TonClient
from src.blockchains.ton.clients.client_manager import TonClientManager
from src.config.config import Config
from src.dependencies.config import get_config

# === === === === === === ===


async def get_ton_client(config: Annotated[Config, Depends(get_config)]) -> TonClient:

    ton_client_manager = TonClientManager(config=config)
    return ton_client_manager.get_ton_client()


# === === === === === === ===
