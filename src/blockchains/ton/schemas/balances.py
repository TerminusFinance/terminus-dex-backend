from typing import Dict

from pydantic import BaseModel
from src.types.ton.ton_address_annotated import TonAddressType

# === === === === === === ===


class Balances(BaseModel):

    jettons: Dict[TonAddressType, int]
    ton: int


# === === === === === === ===
