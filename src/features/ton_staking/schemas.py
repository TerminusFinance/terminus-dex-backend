from pydantic import BaseModel
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.features.ton_common.schemas.ton_prepared_transaction import TonPreparedTransaction
from src.types.ton.ton_address_annotated import TonAddressType

# === === === === === === ===


class TonStakingContractData(BaseModel):

    address: TonAddressType
    in_asset: TonAsset
    out_asset: TonAsset
    apy: float
    fees: float
    min_offer_amount: int
    is_active: bool


# === === === === === === ===


class TonContractStakeData(BaseModel):

    address: TonAddressType
    price: int
    is_active: bool


# === === === === === === ===


class TonStakingPreparedTransactionData(BaseModel):

    transaction: TonPreparedTransaction
    expected_amount: int
