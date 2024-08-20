from typing import Annotated, Any, Dict

from pydantic import BaseModel, BeforeValidator

from src.types.ton import TonAddressType

int16 = Annotated[int, BeforeValidator(lambda v: int(v, 16))]


class TonMessage(BaseModel):

    created_lt: int
    value: int
    destination: TonAddressType | None = None
    source: TonAddressType | None = None
    op_code: int16 | None = None
    decoded_op_name: str | None = None
    decoded_body: Dict[str, Any] | str | None = None
    raw_body: str | None = None
