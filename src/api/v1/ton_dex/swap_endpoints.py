# === === === === === === ===

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.schemas.base_messages import ErrorMessage
from src.api.v1.schemas.liquidity import PrepareTransactionSuccessMessage
from src.api.v1.security_utils import get_account_from_request, validate_auth_token
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.dependencies.ton_client import get_ton_client
from src.features.ton_dex.params_manager import DexParamsManager
from src.features.ton_dex.router_contract import TonDexRouterContract

from ..schemas.swap import GetSwapParamsBody, GetSwapParamsSuccessMessage, SwapParamsBody

# === === === === === === ===

logger = logging.getLogger("SwapEndpointsLogger")

# === === === === === === ===


async def get_swap_params_endpoint(
    request: Request,
    simulate_swap_request_body: GetSwapParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> GetSwapParamsSuccessMessage | ErrorMessage:

    account = await get_account_from_request(request=request, config=config, session=session)

    try:
        dex_params_manager = DexParamsManager(config=config, ton_client=ton_client)
        result = await dex_params_manager.get_swap_params(
            offer_address=simulate_swap_request_body.offer_address,
            ask_address=simulate_swap_request_body.ask_address,
            referral_address=account.affiliate_ton_address if account is not None else None,
            units=simulate_swap_request_body.units,
            slippage_tolerance=simulate_swap_request_body.slippage_tolerance,
            swap_type=simulate_swap_request_body.swap_type,
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return GetSwapParamsSuccessMessage(data=result)


# === === === === === === ===


async def prepare_swap_endpoint(
    request: Request,
    swap_request_body: SwapParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)
    try:
        router = TonDexRouterContract(
            ton_client=ton_client,
            config=config,
            address=config.ton_dex.router_address,
            proxy_ton_address=config.ton_dex.proxy_ton_address,
        )

        transaction_data = await router.prepare_swap_transaction(
            account_address=account.ton_address,
            offer_jetton_address=swap_request_body.offer_address,
            ask_jetton_address=swap_request_body.ask_address,
            offer_units=swap_request_body.offer_units,
            min_ask_units=swap_request_body.min_ask_units,
            referral_address=account.affiliate_ton_address,
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=transaction_data)


# === === === === === === ===
