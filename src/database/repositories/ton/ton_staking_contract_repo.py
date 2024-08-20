from datetime import UTC, datetime
from typing import List

from sqlalchemy import select

from ...database_models.ton.ton_staking_contract import TonStakingContractDb
from ..base_repo import BaseRepository


class TonStakingContractRepository(BaseRepository):

    # === === === Create TonStakingContractDb === === ===
    async def create(
        self,
        address: str,
        in_asset_address: str,
        out_asset_address: str,
        apy: float,
        fees: int,
        min_offer_amount: int,
        is_active: bool,
        needs_flush: bool = False,
    ) -> TonStakingContractDb:

        ton_staking_contract = TonStakingContractDb(
            address=address,
            in_asset_address=in_asset_address,
            out_asset_address=out_asset_address,
            apy=apy,
            fees=fees,
            min_offer_amount=min_offer_amount,
            is_active=is_active,
        )

        self.session.add(ton_staking_contract)

        if needs_flush:
            await self.session.flush()

        return ton_staking_contract

    # === === === Get TonStakingContractDb === === ===
    async def get(
        self,
        id: int | None = None,
        address: str | None = None,
        deleted: bool = False,
    ) -> TonStakingContractDb | None:

        if id is not None:
            ton_staking_contract = await self.session.get(TonStakingContractDb, id)

        if address is not None:
            query = select(TonStakingContractDb).where(TonStakingContractDb.address == address)
            result = await self.session.execute(query)
            ton_staking_contract = result.unique().scalar()

        if not deleted and ton_staking_contract and ton_staking_contract.is_deleted:
            return None

        return ton_staking_contract

    # === === === Update TonStakingContractDb === === ===
    async def update(
        self,
        ton_staking_contract: TonStakingContractDb,
        needs_flush: bool = False,
    ) -> TonStakingContractDb:

        self.session.add(ton_staking_contract)

        if needs_flush:
            await self.session.flush()

        return ton_staking_contract

    # === === === Delete TonStakingContractDb === === ===
    async def delete(
        self,
        ton_staking_contract: TonStakingContractDb,
        needs_flush: bool = False,
    ) -> None:

        if ton_staking_contract.is_deleted:
            return

        ton_staking_contract.is_deleted = True
        ton_staking_contract.deleting_time = datetime.now(UTC)

        self.session.add(ton_staking_contract)

        if needs_flush:
            await self.session.flush()

    # === === === Get All TonStakingContractDb === === ===
    async def get_all(
        self,
        deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TonStakingContractDb]:

        query = select(TonStakingContractDb)

        if deleted:
            query = query.where(TonStakingContractDb.is_deleted == deleted)

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        ton_staking_contracts = list(result.scalars().unique().all())

        return ton_staking_contracts
