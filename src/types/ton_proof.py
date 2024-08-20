from pydantic import BaseModel


# === === === === === === ===
class TonProofDomain(BaseModel):

    length_bytes: int
    value: str


# === === === === === === ===
class TonProof(BaseModel):

    timestamp: int
    domain: TonProofDomain
    signature: str
    payload: str
    state_init: str | None = None
    public_key: str | None = None
