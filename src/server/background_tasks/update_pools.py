# === === === === === === ===

import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker
from src.blockchains.ton.clients import TonClient
from src.config import Config
from src.features.ton_dex.dex_observer import DexObserver

# === === === === === === ===


async def update_pools_interval(
    interval: int,
    sessionmaker: async_sessionmaker,
    config: Config,
    ton_client: TonClient,
):

    while True:
        try:
            async with sessionmaker() as session:

                dex_observer = DexObserver(config=config, ton_client=ton_client, session=session)
                await dex_observer.update_pools()
        except Exception:
            pass
        finally:
            await asyncio.sleep(interval)


# === === === === === === ===
