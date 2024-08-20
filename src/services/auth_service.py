from datetime import UTC, datetime, timedelta
from typing import Tuple

import jwt
from fastapi import Response
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.ton_proof import check_ton_proof
from src.config.config import Config
from src.exceptions.auth_exceptions import AuthTokenExpiredError, InvalidAuthTokenError
from src.models.account import TokenPayload
from src.types.ton_proof import TonProof
from src.utils.ton_address import TonAddress


class AuthService:

    # === === === === === === ===

    def __init__(
        self,
        config: Config,
    ):

        self.config = config

    # === === === === === === ===

    async def check_ton_proof(
        self,
        wallet_address: TonAddress,
        ton_proof: TonProof,
        ton_client: TonClient | None = None,
    ) -> bool:

        return await check_ton_proof(
            wallet_address=wallet_address, ton_proof=ton_proof, ton_client=ton_client
        )

    # === === === === === === ===

    def sign_new_token(
        self,
        wallet_address: str,
    ) -> Tuple[str, TokenPayload]:

        expires_at = int(
            (
                datetime.now(UTC) + timedelta(minutes=self.config.account.token_ttl_minutes)
            ).timestamp()
        )

        token_payload = TokenPayload(account_address=wallet_address, expires_at=expires_at)

        token = jwt.encode(
            payload=token_payload.model_dump(),
            key=self.config.account.token_secret.get_secret_value(),
            algorithm=self.config.account.token_algorithm,
        )

        return (token, token_payload)

    # === === === === === === ===

    def decode_token(
        self,
        token: str,
    ) -> TokenPayload:

        try:
            data = jwt.decode(
                jwt=token,
                key=self.config.account.token_secret.get_secret_value(),
                algorithms=[self.config.account.token_algorithm],
            )
            token_payload = TokenPayload(**data)
            return token_payload
        except Exception:
            raise InvalidAuthTokenError()

    # === === === === === === ===

    def set_cookies_to_response(
        self,
        response: Response,
        token: str,
        token_payload: TokenPayload,
    ) -> None:

        response.set_cookie(
            key=self.config.account.token_cookie_key,
            value=token,
            # httponly=True,
            samesite="strict",
            max_age=self.config.account.token_ttl_minutes * 60,
            expires=token_payload.expires_at,
            secure=True,
            path="/",
        )

    # === === === === === === ===

    def check_token(
        self,
        token: str,
    ) -> TokenPayload:

        token_payload = self.decode_token(token=token)

        if token_payload.expires_at < int(datetime.now(UTC).timestamp()):
            raise AuthTokenExpiredError()

        return token_payload

    # === === === === === === ===

    def reset_token_cookie(
        self,
        response: Response,
    ) -> None:

        response.set_cookie(
            key=self.config.account.token_cookie_key,
            value="",
            # httponly=True,
            samesite="strict",
            max_age=0,
            expires=0,
            secure=True,
            path="/",
        )

    # === === === === === === ===
