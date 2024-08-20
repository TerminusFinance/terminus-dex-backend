from enum import StrEnum

from pydantic import BaseModel
from src.types.ton.ton_address_annotated import TonAddressType

# === === === === === === ===


class LpAccountData(BaseModel):

    owner_address: TonAddressType
    pool_address: TonAddressType
    token_0_balance: int
    token_1_balance: int


# === === === === === === ===


class PoolData(BaseModel):

    address: TonAddressType
    reserve_0: int
    reserve_1: int
    token_0_address: TonAddressType
    token_1_address: TonAddressType
    lp_fee: int
    protocol_fee: int
    ref_fee: int
    protocol_fee_address: TonAddressType
    collected_token_0_protocol_fee: int
    collected_token_1_protocol_fee: int


# === === === === === === ===


class ExpectedLiquidityData(BaseModel):

    token_0_amount: int
    token_1_amount: int


# === === === === === === ===


class TonSwapParams(BaseModel):

    ask_address: TonAddressType
    ask_units: int
    fee_address: TonAddressType
    fee_percent: float
    fee_units: int
    min_ask_units: int
    offer_address: TonAddressType
    offer_units: int
    pool_address: TonAddressType
    price_impact: float
    router_address: TonAddressType
    slippage_tolerance: float
    swap_rate: float
    min_fee: int
    max_fee: int


# === === === === === === ===


class TonProvideAction(StrEnum):

    PROVIDE = "provide"
    PROVIDE_SECOND = "provide_second"
    PROVIDE_ADDITIONAL = "provide_additional"
    PROVIDE_DIRECT = "provide_direct"
    CREATE_POOL = "create_pool"
    INIT_POOL = "init_pool"


# === === === === === === ===


class TonBaseProvideLiquidityParams(BaseModel):

    action: TonProvideAction
    first_token_address: TonAddressType
    second_token_address: TonAddressType
    first_token_units: int
    second_token_units: int
    pool_address: TonAddressType
    lp_account_address: TonAddressType | None = None
    lp_balance: int | None = None
    fee_min: int | None = None  # TODO: Make it required
    fee_max: int | None = None  # TODO: Make it required


# === === === === === === ===


class TonProvideCommonParams(BaseModel):

    first_token_units: int
    second_token_units: int
    expected_lp_units: int
    min_expected_lp_units: int
    slippage_tolerance: float
    estimated_share_of_pool: float


# === === === === === === ===


class TonProvideLiquidityParams(TonBaseProvideLiquidityParams):

    first_token_balance: int | None = None
    second_token_balance: int | None = None
    slippage_tolerance: float
    expected_lp_units: int
    min_expected_lp_units: int
    estimated_share_of_pool: float
    send_token_address: TonAddressType | None = None
    send_units: int | None = None


# === === === === === === ===


class TonCreateLiquidityPoolParams(TonBaseProvideLiquidityParams):

    action: TonProvideAction = TonProvideAction.CREATE_POOL


# === === === === === === ===
