from typing import Any, List

from pydantic import BaseModel


class StackRecord(BaseModel):

    type: str
    cell: str | None
    slice: str | None
    num: str | None
    tuple: List["StackRecord"] | None


class GetMethodResult(BaseModel):
    success: bool
    exit_code: int
    stack: List[StackRecord]
    decoded: Any | None
