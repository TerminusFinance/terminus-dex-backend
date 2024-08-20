from typing import Annotated

from fastapi import Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.security_utils import validate_auth_token
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.schemas.balances import Balances
from src.config.config import Config
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.dependencies.ton_client import get_ton_client
from src.utils.ton_address import TonAddress

# === === === === === === ===


async def get_balances(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
    account_address: str = Path(),
) -> Balances:

    await validate_auth_token(
        account_address=account_address, request=request, config=config, session=session
    )

    balances = await ton_client.get_balances(account_address=TonAddress(account_address))

    return balances


# === === === === === === ===
