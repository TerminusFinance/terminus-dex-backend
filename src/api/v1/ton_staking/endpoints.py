# === === === === === === ===

from typing import Annotated, List

from fastapi import Body, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.dependencies.ton_client import get_ton_client
from src.features.ton_staking.schemas import (
    TonContractStakeData,
    TonStakingContractData,
    TonStakingPreparedTransactionData,
)
from src.services.ton.ton_staking_service import TonStakingService
from src.utils.ton_address import TonAddress

# === === === === === === ===


async def get_staking_pools(
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> List[TonStakingContractData]:

    try:
        ton_staking_service = TonStakingService(
            session=session, config=config, ton_client=ton_client
        )
        staking_contracts_data = await ton_staking_service.get_staking_contracts_data()
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return staking_contracts_data


# === === === === === === ===


async def get_stake_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
    contract_address: str = Path(),
) -> TonContractStakeData:

    try:
        ton_staking_service = TonStakingService(
            session=session, config=config, ton_client=ton_client
        )
        stake_data = await ton_staking_service.get_contract_stake_data(
            contract_address=TonAddress(contract_address)
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return stake_data


# === === === === === === ===


async def get_prepared_transaction_data(
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
    contract_address: str = Path(),
    offer_amount: int = Body(),
) -> TonStakingPreparedTransactionData:

    try:
        ton_staking_service = TonStakingService(
            session=session, config=config, ton_client=ton_client
        )
        prepared_transaction_data = await ton_staking_service.get_prepared_stake_transaction(
            contract_address=TonAddress(contract_address), offer_amount=offer_amount
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return prepared_transaction_data


# === === === === === === ===
