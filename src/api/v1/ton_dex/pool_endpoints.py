# === === === === === === ===

from typing import Annotated, List, Tuple

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.dependencies.ton_client import get_ton_client
from src.services.ton.ton_dex_service import TonDexService

# === === === === === === ===


async def get_assets_pairs_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> List[Tuple[str, str]]:

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        assets_pairs = await dex_service.get_assets_pairs()
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return assets_pairs


# === === === === === === ===
