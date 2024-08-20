from pydantic import BaseModel
from src.blockchains.ton.schemas.ton_jetton_info import TonJettonInfo
from src.database.database_models.ton.ton_dex_asset import TonAssetDb
from src.types.ton.ton_address_annotated import TonAddressType
from src.utils.ton_address import TonAddress


class TonAsset(BaseModel):

    address: TonAddressType
    symbol: str
    name: str
    image_url: str | None = None
    decimals: int

    is_whitelisted: bool
    is_community: bool
    is_deprecated: bool
    is_blacklisted: bool

    # === === === === === === ===

    @staticmethod
    def from_db_model(ton_asset: TonAssetDb) -> "TonAsset":

        return TonAsset(
            address=TonAddress(ton_asset.address),
            symbol=ton_asset.symbol,
            name=ton_asset.name,
            image_url=ton_asset.image_url,
            decimals=ton_asset.decimals,
            is_whitelisted=ton_asset.is_whitelisted,
            is_community=ton_asset.is_community,
            is_deprecated=ton_asset.is_deprecated,
            is_blacklisted=ton_asset.is_blacklisted,
        )

    # === === === === === === ===

    @staticmethod
    def from_jetton_info(jetton_info: TonJettonInfo) -> "TonAsset":

        return TonAsset(
            address=TonAddress(jetton_info.address),
            symbol=jetton_info.symbol,
            name=jetton_info.name,
            image_url=jetton_info.image_url,
            decimals=jetton_info.decimals,
            is_whitelisted=jetton_info.is_whitelisted,
            is_community=jetton_info.is_community,
            is_deprecated=False,
            is_blacklisted=jetton_info.is_blacklisted,
        )

    # === === === === === === ===
