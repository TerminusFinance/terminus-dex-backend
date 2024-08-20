from pydantic import BaseModel
from src.api.v1.schemas.base_messages import SuccessMessage
from src.features.ton_dex.params_manager import SwapType
from src.features.ton_dex.schemas import TonSwapParams
from src.utils.ton_address import ValidatedAddress

# === === === === === === ===


class SwapParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    # === === === === === === ===

    offer_address: ValidatedAddress
    ask_address: ValidatedAddress
    offer_units: int
    min_ask_units: int
    slippage_tolerance: float
    swap_type: str


# === === === === === === ===


class GetSwapParamsBody(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    # === === === === === === ===

    offer_address: ValidatedAddress
    ask_address: ValidatedAddress
    units: int
    slippage_tolerance: float
    swap_type: SwapType


# === === === === === === ===


class GetSwapParamsSuccessMessage(SuccessMessage):

    data: TonSwapParams


# === === === === === === ===
