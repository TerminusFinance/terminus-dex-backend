from typing import List

from pydantic import BaseModel

# === === === === === === ===


class TonPreparedMessage(BaseModel):
    address: str
    amount: int
    payload: str | None = None


# === === === === === === ===


class TonPreparedTransaction(BaseModel):

    valid_until: int
    network: int
    messages: List[TonPreparedMessage]


# === === === === === === ===
