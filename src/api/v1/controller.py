from fastapi import APIRouter

from .account.controller import account_router
from .ton_dex.controller import ton_dex_router
from .ton_staking.controller import staking_router

# === === === === === === ===


# === === === === === === ===

api_v1_router = APIRouter(
    include_in_schema=True,
)

# === === === === === === ===

api_v1_router.include_router(account_router, prefix="/account", tags=["account"])
api_v1_router.include_router(staking_router, prefix="/ton-staking", tags=["staking", "ton"])
api_v1_router.include_router(ton_dex_router, prefix="/ton-dex", tags=["dex", "ton"])

# === === === === === === ===
