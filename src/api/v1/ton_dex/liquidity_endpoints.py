# === === === === === === ===

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.schemas.base_messages import ErrorMessage
from src.api.v1.schemas.liquidity import (
    GetProvideLiquidityParamsBody,
    GetProvideLiquidityParamsSuccessMessage,
    PrepareActivateLiquidityParamsBody,
    PrepareCreatePoolParamsBody,
    PrepareProvideLiquidityParamsBody,
    PrepareProvideSingleSideParamsBody,
    PrepareRefundLiquidityParamsBody,
    PrepareRemoveLiquidityParamsBody,
    PrepareTransactionSuccessMessage,
)
from src.api.v1.security_utils import get_account_from_request, validate_auth_token
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.dependencies.ton_client import get_ton_client
from src.services.ton.ton_dex_service import TonDexService

# === === === === === === ===

logger = logging.getLogger("LiquidityEndpointsLogger")

# === === === === === === ===


async def get_provide_liquidity_params_endpoint(
    request: Request,
    request_body: GetProvideLiquidityParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> GetProvideLiquidityParamsSuccessMessage | ErrorMessage:

    account = await get_account_from_request(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.get_provide_liquidity_params(
            first_token_address=request_body.first_token_address,
            second_token_address=request_body.second_token_address,
            first_token_units=request_body.first_token_units,
            second_token_units=request_body.second_token_units,
            slippage_tolerance=request_body.slippage_tolerance,
            first_is_base=request_body.is_first_base,
            account_address=account.ton_address if account is not None else None,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return GetProvideLiquidityParamsSuccessMessage(data=params)


# === === === === === === ===


async def prepare_create_pool_endpoint(
    request: Request,
    request_body: PrepareCreatePoolParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.prepare_create_pool_transaction(
            first_token_address=request_body.first_token_address,
            second_token_address=request_body.second_token_address,
            first_token_units=request_body.first_token_units,
            second_token_units=request_body.second_token_units,
            account_address=account.ton_address,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=params)


# === === === === === === ===


async def prepare_provide_liquidity_transaction_endpoint(
    request: Request,
    request_body: PrepareProvideLiquidityParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.prepare_provide_liquidity_transaction(
            first_token_address=request_body.first_token_address,
            second_token_address=request_body.second_token_address,
            first_token_units=request_body.first_token_units,
            second_token_units=request_body.second_token_units,
            account_address=account.ton_address,
            min_lp_out_units=request_body.min_lp_out_units,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=params)


# === === === === === === ===


async def prepare_provide_single_side_transaction_endpoint(
    request: Request,
    request_body: PrepareProvideSingleSideParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.prepare_provide_single_side_transaction(
            send_token_address=request_body.send_token_address,
            second_token_address=request_body.second_token_address,
            send_units=request_body.send_units,
            min_lp_out_units=request_body.min_lp_out_units,
            account_address=account.ton_address,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=params)


# === === === === === === ===


async def prepare_activate_liquidity_endpoint(
    request: Request,
    request_body: PrepareActivateLiquidityParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.prepare_activate_liquidity_transaction(
            first_token_address=request_body.first_token_address,
            second_token_address=request_body.second_token_address,
            first_token_units=request_body.first_token_units,
            second_token_units=request_body.second_token_units,
            min_lp_out_units=request_body.min_lp_out_units,
            account_address=account.ton_address,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=params)


# === === === === === === ===


async def prepare_refund_liquidity_endpoint(
    request: Request,
    request_body: PrepareRefundLiquidityParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.prepare_refund_liquidity_transaction(
            first_token_address=request_body.first_token_address,
            second_token_address=request_body.second_token_address,
            account_address=account.ton_address,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=params)


# === === === === === === ===


async def prepare_remove_liquidity_endpoint(
    request: Request,
    request_body: PrepareRemoveLiquidityParamsBody,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> PrepareTransactionSuccessMessage | ErrorMessage:

    account = await validate_auth_token(request=request, config=config, session=session)

    try:
        dex_service = TonDexService(session=session, config=config, ton_client=ton_client)
        params = await dex_service.prepare_burn_liquidity_transaction(
            account_address=account.ton_address,
            first_token_address=request_body.first_token_address,
            second_token_address=request_body.second_token_address,
            lp_units=request_body.lp_units,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return PrepareTransactionSuccessMessage(data=params)


# === === === === === === ===
