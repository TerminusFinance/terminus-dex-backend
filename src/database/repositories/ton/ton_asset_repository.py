from datetime import UTC, datetime
from typing import List

from sqlalchemy import select
from src.utils.ton_address import TonAddress

from ...database_models.ton import TonAssetDb
from ..base_repo import BaseRepository


class TonAssetRepository(BaseRepository):

    # === === === Create TonAssetDb === === ===
    async def create(
        self,
        address: TonAddress,
        name: str,
        symbol: str,
        decimals: int,
        image_url: str | None = None,
        is_whitelisted: bool = False,
        is_community: bool = False,
        is_deprecated: bool = False,
        is_blacklisted: bool = False,
        needs_flush: bool = False,
        account_address: TonAddress | None = None,
    ) -> TonAssetDb:

        ton_asset = TonAssetDb(
            address=address.to_string(),
            name=name,
            symbol=symbol,
            decimals=decimals,
            image_url=image_url,
            is_whitelisted=is_whitelisted,
            is_community=is_community,
            is_deprecated=is_deprecated,
            is_blacklisted=is_blacklisted,
            account_address=account_address.to_string() if account_address else None,
        )

        self.session.add(ton_asset)

        if needs_flush:
            await self.session.flush()

        return ton_asset

    # === === === Get TonAssetDb === === ===
    async def get(
        self,
        id: int | None = None,
        address: TonAddress | None = None,
        deleted: bool = False,
    ) -> TonAssetDb | None:

        if not id and not address:
            return None

        if id is not None:
            query = select(TonAssetDb).where(TonAssetDb.id == id)

        if address is not None:
            query = select(TonAssetDb).where(TonAssetDb.address == address.to_string())

        result = await self.session.execute(query)
        ton_asset = result.scalar_one_or_none()

        if not deleted and ton_asset and ton_asset.is_deleted:
            return None

        return ton_asset

    # === === === Update TonAssetDb === === ===
    async def update(
        self,
        address: TonAddress,
        name: str,
        symbol: str,
        decimals: int,
        image_url: str | None = None,
        is_whitelisted: bool = False,
        is_community: bool = False,
        is_deprecated: bool = False,
        is_blacklisted: bool = False,
        needs_flush: bool = False,
    ) -> TonAssetDb | None:

        ton_asset = await self.get(address=address)

        if not ton_asset:
            return None

        ton_asset.name = name
        ton_asset.symbol = symbol
        ton_asset.decimals = decimals
        ton_asset.image_url = image_url
        ton_asset.is_whitelisted = is_whitelisted
        ton_asset.is_community = is_community
        ton_asset.is_deprecated = is_deprecated
        ton_asset.is_blacklisted = is_blacklisted

        self.session.add(ton_asset)

        if needs_flush:
            await self.session.flush()

        return ton_asset

    # === === === Delete TonAssetDb === === ===
    async def delete(
        self,
        id: int | None = None,
        address: TonAddress | None = None,
        asset: TonAssetDb | None = None,
        needs_flush: bool = False,
    ) -> bool:

        if not asset:
            asset = await self.get(id=id, address=address)

        if not asset:
            return False

        asset.is_deleted = True
        asset.deleting_time = datetime.now(UTC)

        self.session.add(asset)

        if needs_flush:
            await self.session.flush()

        return True

    # === === === Get All TonAssetDb === === ===
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        all: bool = False,
        exclude_community: bool = False,
        exclude_deprecated: bool = True,
        exclude_blacklisted: bool = True,
        exclude_deleted: bool = True,
    ) -> List[TonAssetDb]:

        query = select(TonAssetDb)

        if exclude_community:
            query = query.where(TonAssetDb.is_community.is_not(True))
        if exclude_deprecated:
            query = query.where(TonAssetDb.is_deprecated.Is_not(True))
        if exclude_blacklisted:
            query = query.where(TonAssetDb.is_blacklisted.is_not(True))
        if exclude_deleted:
            query = query.where(TonAssetDb.is_deleted.is_not(True))

        query = query.order_by(TonAssetDb.id)

        if not all:
            query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        assets = list(result.unique().scalars().all())

        return assets

    # === === ===  === === ===
