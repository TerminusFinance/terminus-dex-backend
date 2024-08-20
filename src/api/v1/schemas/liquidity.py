from pydantic import BaseModel
from src.api.v1.schemas.base_messages import SuccessMessage
from src.features.ton_common.schemas.ton_prepared_transaction import TonPreparedTransaction
from src.features.ton_dex.schemas import TonBaseProvideLiquidityParams, TonProvideLiquidityParams
from src.utils.ton_address import ValidatedAddress, ValidatedAddressOrNone

# === === === === === === ===


class GetProvideLiquidityParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    first_token_address: ValidatedAddress
    second_token_address: ValidatedAddress
    first_token_units: int
    second_token_units: int
    slippage_tolerance: float
    is_first_base: bool
    lp_account_address: ValidatedAddressOrNone = None


# === === === === === === ===


class GetProvideLiquidityParamsSuccessMessage(SuccessMessage):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    data: TonBaseProvideLiquidityParams | TonProvideLiquidityParams


# === === === === === === ===


class PrepareCreatePoolParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    first_token_address: ValidatedAddress
    second_token_address: ValidatedAddress
    first_token_units: int
    second_token_units: int


# === === === === === === ===


class PrepareTransactionSuccessMessage(SuccessMessage):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    data: TonPreparedTransaction


# === === === === === === ===


class PrepareProvideLiquidityParamsBody(PrepareCreatePoolParamsBody):

    min_lp_out_units: int


# === === === === === === ===


class PrepareProvideSingleSideParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    send_token_address: ValidatedAddress
    second_token_address: ValidatedAddress
    send_units: int
    min_lp_out_units: int


# === === === === === === ===


class PrepareActivateLiquidityParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    first_token_address: ValidatedAddress
    second_token_address: ValidatedAddress
    first_token_units: int
    second_token_units: int
    min_lp_out_units: int


# === === === === === === ===


class PrepareRemoveLiquidityParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    first_token_address: ValidatedAddress
    second_token_address: ValidatedAddress
    lp_units: int


# === === === === === === ===


class PrepareRefundLiquidityParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    first_token_address: ValidatedAddress
    second_token_address: ValidatedAddress


# === === === === === === ===
