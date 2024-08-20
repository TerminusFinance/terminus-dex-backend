from pydantic import BaseModel
from src.types.ton_proof import TonProof
from src.utils.ton_address import ValidatedAddress


class AuthRequest(BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    referral_code: str | None = None
    address: ValidatedAddress
    proof: TonProof
    tg_init_data: str | None = None
