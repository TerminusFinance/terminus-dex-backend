from datetime import UTC, datetime, timedelta
from typing import Callable

from fastapi.requests import Request
from fastapi.responses import Response
from src.config import ConfigManager
from src.exceptions.auth_exceptions import AuthTokenExpiredError, InvalidAuthTokenError
from src.services import AuthService

# === === === === === === ===


async def auth_middleware(
    request: Request,
    call_next: Callable,
):

    config = ConfigManager().get_config()

    token = request.cookies.get(config.account.token_cookie_key, None)
    response: Response = await call_next(request)

    if not token:
        return response

    auth_service = AuthService(config=config)

    try:
        token_payload = auth_service.decode_token(token=token)
        current_time = datetime.now(UTC)
        if token_payload.expires_at < int(current_time.timestamp()):
            raise AuthTokenExpiredError()

        if current_time - datetime.fromtimestamp(token_payload.expires_at, UTC) < timedelta(
            minutes=config.account.token_update_threshold_minutes
        ):
            new_token, new_token_payload = auth_service.sign_new_token(
                wallet_address=token_payload.account_address
            )
            auth_service.set_cookies_to_response(
                response=response, token=new_token, token_payload=new_token_payload
            )

    except AuthTokenExpiredError | InvalidAuthTokenError:
        auth_service.reset_token_cookie(response=response)

    return response


# === === === === === === ===
