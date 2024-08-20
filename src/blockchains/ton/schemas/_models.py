# === === === === === === ===

from pydantic import BaseModel
from src.types.ton import TonAddressType

# === === === === === === ===


class MessageBody(BaseModel):

    text: str | None = None


# === === === === === === ===


class JettonMessageBodyForwardPayloadValue(BaseModel):

    sum_type: str | None = None
    op_code: int | None = None
    value: MessageBody | None = None


# === === === === === === ===


class JettonMessageBodyForwardPayload(BaseModel):

    is_right: bool
    value: JettonMessageBodyForwardPayloadValue


# === === === === === === ===


class JettonMessageBody(BaseModel):

    query_id: int
    amount: int
    destination: TonAddressType
    response_destination: TonAddressType
    custom_payload: str | None
    forward_ton_amount: int

    forward_payload: JettonMessageBodyForwardPayload


# === === === === === === ===


class JettonTransferNotificationMessageBody(BaseModel):

    query_id: int
    amount: int
    sender: TonAddressType
    forward_payload: JettonMessageBodyForwardPayload


# === === === === === === ===


class JettonWalletData(BaseModel):

    jetton_wallet_address: TonAddressType
    balance: int
    jetton_contract_address: TonAddressType
    owner_wallet_address: TonAddressType


# === === === === === === ===


class JettonData(BaseModel):

    total_supply: int
    admin_address: TonAddressType
    mintable: bool


# === === === === === === ===


class TonAccountInfo(BaseModel):

    address: TonAddressType
    ton_balance: int
    status: str


# === === === === === === ===
