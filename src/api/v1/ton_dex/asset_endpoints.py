from typing import Annotated, List

from fastapi import Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.schemas.base_messages import ErrorMessage
from src.api.v1.security_utils import get_account_from_request
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.constants.api_message_code import ApiMessageCode
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.dependencies.ton_client import get_ton_client
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.services.ton.ton_dex_service import TonDexService
from src.utils.ton_address import validate_address_or_none

# === === === === === === ===


async def get_assets(
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> List[TonAsset]:

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        assets = await dex_service.get_assets()
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return assets


# === === === === === === ===


async def find_new_asset(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
    address: str = Path(),
) -> TonAsset | ErrorMessage:

    account = await get_account_from_request(request=request, session=session, config=config)

    ton_address = validate_address_or_none(address=address)
    if not ton_address:
        return ErrorMessage(code=ApiMessageCode.INVALID_TON_ADDRESS, error="Invalid TON address")

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        asset = await dex_service.find_asset(
            address=ton_address, account_address=account.ton_address if account else None
        )

        if asset is None:
            return ErrorMessage(
                code=ApiMessageCode.TON_DEX_ASSET_NOT_FOUND, error="Asset not found"
            )

        await session.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return asset


# === === === === === === ===
