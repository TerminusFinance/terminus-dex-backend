from pydantic import BaseModel


class TokenPayload(BaseModel):

    account_address: str
    expires_at: int
