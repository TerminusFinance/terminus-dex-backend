from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from src.database.database_models.ton.ton_dex_pool import TonDexPoolDb
from src.types.ton.ton_address_annotated import TonAddressType
from src.utils.ton_address import TonAddress

if TYPE_CHECKING:
    from .ton_asset import TonAsset

# === === === === === === ===


class TonDexPool(BaseModel):

    id: int
    address: TonAddressType
    reserve_0: int
    reserve_1: int
    token_0_wallet_address: TonAddressType
    token_1_wallet_address: TonAddressType
    lp_fee: int
    protocol_fee: int
    ref_fee: int
    protocol_fee_address: TonAddressType
    collected_token_0_protocol_fee: int
    collected_token_1_protocol_fee: int
    total_supply: int

    asset_0: "TonAsset | None" = Field(exclude=True, default=None)
    asset_1: "TonAsset | None" = Field(exclude=True, default=None)

    # === === === === === === ===

    @staticmethod
    def from_db_model(
        ton_dex_pool: TonDexPoolDb,
        asset_0: "TonAsset | None" = None,
        asset_1: "TonAsset | None" = None,
    ) -> "TonDexPool":

        return TonDexPool(
            id=ton_dex_pool.id,
            address=TonAddress(ton_dex_pool.address),
            reserve_0=ton_dex_pool.reserve_0,
            reserve_1=ton_dex_pool.reserve_1,
            token_0_wallet_address=TonAddress(ton_dex_pool.token_0_wallet_address),
            token_1_wallet_address=TonAddress(ton_dex_pool.token_1_wallet_address),
            lp_fee=ton_dex_pool.lp_fee,
            protocol_fee=ton_dex_pool.protocol_fee,
            ref_fee=ton_dex_pool.ref_fee,
            protocol_fee_address=TonAddress(ton_dex_pool.protocol_fee_address),
            collected_token_0_protocol_fee=ton_dex_pool.collected_token_0_protocol_fee,
            collected_token_1_protocol_fee=ton_dex_pool.collected_token_1_protocol_fee,
            total_supply=ton_dex_pool.total_supply,
            asset_0=asset_0,
            asset_1=asset_1,
        )

    # === === === === === === ===
