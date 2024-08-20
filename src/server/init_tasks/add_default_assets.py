# === === === === === === ===

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.blockchains.ton.constants import TonConstants
from src.database.database_models.ton.ton_dex_asset import TonAssetDb
from src.utils.ton_address import TonAddress

# === === === === === === ===

default_assets = [
    TonAssetDb(
        address=TonAddress(TonConstants.ContractAddresses.TON).to_string(),
        name="Toncoin",
        symbol="TON",
        decimals=9,
        image_url="/static/images/icons/128/TON-128.png",
        is_whitelisted=True,
        is_community=False,
        is_blacklisted=False,
        is_deprecated=False,
    )
]

# === === === === === === ===


async def add_default_assets(
    sessionmaker: async_sessionmaker,
) -> None:

    async with sessionmaker() as session:
        session: AsyncSession
        for asset in default_assets:
            query = select(TonAssetDb).where(TonAssetDb.address == asset.address)
            existing_asset = (await session.execute(query)).scalar_one_or_none()
            if not existing_asset:
                session.add(asset)
            else:
                existing_asset.image_url = asset.image_url
                session.add(existing_asset)

        await session.commit()


# === === === === === === ===
