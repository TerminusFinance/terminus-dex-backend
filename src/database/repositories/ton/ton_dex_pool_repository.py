# === === === === === === ===

from datetime import UTC, datetime
from typing import List

from sqlalchemy import select
from src.database.database_models.ton.ton_dex_pool import TonDexPoolDb
from src.database.repositories.base_repo import BaseRepository
from src.utils.ton_address import TonAddress

# === === === === === === ===


class TonDexPoolRepository(BaseRepository):

    # === === === === === === ===

    async def create(
        self,
        address: TonAddress,
        reserve_0: int,
        reserve_1: int,
        token_0_minter_address: TonAddress,
        token_1_minter_address: TonAddress,
        token_0_wallet_address: TonAddress,
        token_1_wallet_address: TonAddress,
        lp_fee: int,
        protocol_fee: int,
        ref_fee: int,
        protocol_fee_address: TonAddress,
        collected_token_0_protocol_fee: int,
        collected_token_1_protocol_fee: int,
        total_supply: int,
        needs_flush: bool = False,
    ) -> TonDexPoolDb:

        pool = TonDexPoolDb(
            address=address.to_string(),
            reserve_0=reserve_0,
            reserve_1=reserve_1,
            token_0_minter_address=token_0_minter_address.to_string(),
            token_1_minter_address=token_1_minter_address.to_string(),
            token_0_wallet_address=token_0_wallet_address.to_string(),
            token_1_wallet_address=token_1_wallet_address.to_string(),
            lp_fee=lp_fee,
            protocol_fee=protocol_fee,
            ref_fee=ref_fee,
            protocol_fee_address=protocol_fee_address.to_string(),
            collected_token_0_protocol_fee=collected_token_0_protocol_fee,
            collected_token_1_protocol_fee=collected_token_1_protocol_fee,
            total_supply=total_supply,
        )

        self.session.add(pool)
        if needs_flush:
            await self.session.flush()

        return pool

    # === === === === === === ===

    async def get(
        self,
        id: int | None = None,
        address: TonAddress | None = None,
        deleted: bool = False,
    ) -> TonDexPoolDb | None:

        if not id and not address:
            return None

        query = select(TonDexPoolDb)

        if id:
            query = query.where(TonDexPoolDb.id == id)

        if address:
            query = query.where(TonDexPoolDb.address == address.to_string())

        if not deleted:
            query = query.where(TonDexPoolDb.is_deleted.is_(False))

        result = await self.session.execute(query)
        pool = result.scalar_one_or_none()

        return pool

    # === === === === === === ===

    async def update(
        self,
        address: TonAddress,
        reserve_0: int,
        reserve_1: int,
        lp_fee: int,
        protocol_fee: int,
        ref_fee: int,
        collected_token_0_protocol_fee: int,
        collected_token_1_protocol_fee: int,
        total_supply: int,
        needs_flush: bool = False,
    ) -> TonDexPoolDb | None:

        pool = await self.get(address=address)
        if not pool:
            return None

        pool.reserve_0 = reserve_0
        pool.reserve_1 = reserve_1
        pool.lp_fee = lp_fee
        pool.protocol_fee = protocol_fee
        pool.ref_fee = ref_fee
        pool.collected_token_0_protocol_fee = collected_token_0_protocol_fee
        pool.collected_token_1_protocol_fee = collected_token_1_protocol_fee
        pool.total_supply = total_supply

        self.session.add(pool)

        if needs_flush:
            await self.session.flush()

        return pool

    # === === === === === === ===

    async def delete(
        self,
        id: int,
        address: TonAddress,
        pool: TonDexPoolDb | None = None,
        needs_flush: bool = False,
    ) -> bool:

        pool = await self.get(id=id, address=address)
        if not pool:
            return False

        pool.is_deleted = True
        pool.deleting_time = datetime.now(UTC)

        if needs_flush:
            await self.session.flush()

        return True

    # === === === === === === ===

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        all: bool = True,
        exclude_deleted: bool = True,
    ) -> List[TonDexPoolDb]:

        query = select(TonDexPoolDb)

        if exclude_deleted:
            query = query.where(TonDexPoolDb.is_deleted.is_(False))

        query.order_by(TonDexPoolDb.id)

        if not all:
            query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        pools = list(result.scalars().all())

        return pools

    # === === === === === === ===
