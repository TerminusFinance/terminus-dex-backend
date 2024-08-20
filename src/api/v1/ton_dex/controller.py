# === === === === === === ===

from typing import List, Tuple

from fastapi import APIRouter
from src.api.v1.schemas.liquidity import (
    GetProvideLiquidityParamsSuccessMessage,
    PrepareTransactionSuccessMessage,
)
from src.api.v1.schemas.swap import GetSwapParamsSuccessMessage
from src.api.v1.ton_dex.liquidity_endpoints import (
    get_provide_liquidity_params_endpoint,
    prepare_activate_liquidity_endpoint,
    prepare_create_pool_endpoint,
    prepare_provide_liquidity_transaction_endpoint,
    prepare_provide_single_side_transaction_endpoint,
    prepare_refund_liquidity_endpoint,
    prepare_remove_liquidity_endpoint,
)
from src.api.v1.ton_dex.pool_endpoints import get_assets_pairs_endpoint
from src.features.ton_common.schemas.ton_asset import TonAsset

from ..schemas.base_messages import ErrorMessage
from .asset_endpoints import find_new_asset, get_assets
from .swap_endpoints import get_swap_params_endpoint, prepare_swap_endpoint

# === === === === === === ===

ton_dex_router = APIRouter()

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/asset/{address}/find",
    endpoint=find_new_asset,
    methods=["GET"],
    response_model=TonAsset | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/swap/prepare",
    endpoint=prepare_swap_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/swap/params",
    endpoint=get_swap_params_endpoint,
    methods=["POST"],
    response_model=GetSwapParamsSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/params",
    endpoint=get_provide_liquidity_params_endpoint,
    methods=["POST"],
    response_model=GetProvideLiquidityParamsSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/create-pool",
    endpoint=prepare_create_pool_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/provide",
    endpoint=prepare_provide_liquidity_transaction_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/provide-single-side",
    endpoint=prepare_provide_single_side_transaction_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/activate",
    endpoint=prepare_activate_liquidity_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/refund",
    endpoint=prepare_refund_liquidity_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/liquidity/remove",
    endpoint=prepare_remove_liquidity_endpoint,
    methods=["POST"],
    response_model=PrepareTransactionSuccessMessage | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/assets",
    endpoint=get_assets,
    methods=["GET"],
    response_model=List[TonAsset] | ErrorMessage,
)

# === === === === === === ===

ton_dex_router.add_api_route(
    path="/assets/pairs",
    endpoint=get_assets_pairs_endpoint,
    methods=["GET"],
    response_model=List[Tuple[str, str]] | ErrorMessage,
)

# === === === === === === ===
