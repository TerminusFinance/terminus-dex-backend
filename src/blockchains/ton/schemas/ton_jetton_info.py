from pydantic import BaseModel
from src.types.ton.ton_address_annotated import TonAddressType


class TonJettonInfo(BaseModel):

    address: TonAddressType
    name: str
    symbol: str
    decimals: int
    image_url: str | None = None

    is_whitelisted: bool
    is_community: bool
    is_blacklisted: bool
