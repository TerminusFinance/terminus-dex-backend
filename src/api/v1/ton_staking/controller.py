from typing import List

from fastapi import APIRouter
from src.features.ton_staking.schemas import TonContractStakeData, TonStakingContractData

from .endpoints import get_stake_data, get_staking_pools

# === === === === === === ===

staking_router = APIRouter()

# === === === === === === ===

staking_router.add_api_route(
    path="/pools",
    endpoint=get_staking_pools,
    methods=["GET"],
    response_model=List[TonStakingContractData],
)

# === === === === === === ===

staking_router.add_api_route(
    path="/pool/{contract_address}/data",
    endpoint=get_stake_data,
    methods=["GET"],
    response_model=TonContractStakeData,
)

# === === === === === === ===
