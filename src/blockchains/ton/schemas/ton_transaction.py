from typing import List

from pydantic import BaseModel

from src.types.ton import TonAddressType

from .ton_message import TonMessage


class TonTransaction(BaseModel):

    block_id: str
    hash: str
    lt: int
    account: TonAddressType
    utime: int
    in_msg: TonMessage | None = None
    out_msgs: List[TonMessage]
