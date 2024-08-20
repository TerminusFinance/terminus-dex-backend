from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.config import Config
from src.exceptions.auth_exceptions import InvalidAuthTokenError
from src.models.account import Account
from src.services.account_service import AccountService
from src.services.auth_service import AuthService
from src.utils.ton_address import TonAddress

# === === === === === === ===


async def get_account_from_request(
    request: Request,
    config: Config,
    session: AsyncSession,
) -> Account | None:

    token = request.cookies.get(config.account.token_cookie_key, None)
    if not token:
        return None

    auth_service = AuthService(config=config)
    try:
        payload = auth_service.decode_token(token=token)
    except InvalidAuthTokenError:
        return None

    account_service = AccountService(session=session, config=config)
    account = await account_service.get_account(ton_address=TonAddress(payload.account_address))

    return account


# === === === === === === ===


async def validate_auth_token(
    request: Request,
    config: Config,
    session: AsyncSession,
    account_address: str | None = None,
) -> Account:

    token = request.cookies.get(config.account.token_cookie_key, None)
    if not token:
        raise HTTPException(status_code=403, detail="Access Denied! No token provided.")

    auth_service = AuthService(config=config)
    try:
        payload = auth_service.decode_token(token=token)
    except InvalidAuthTokenError:
        raise HTTPException(status_code=403, detail="Access Denied! Invalid token.")

    req_account_address: TonAddress | None = None
    try:
        token_account_address = TonAddress(payload.account_address)
        if account_address:
            req_account_address = TonAddress(account_address)
    except Exception:
        raise HTTPException(status_code=403, detail="Wrong address! Invalid address.")

    if req_account_address and token_account_address != req_account_address:
        raise HTTPException(status_code=403, detail="Access Denied! Addresses do not match.")

    account_service = AccountService(session=session, config=config)
    account = await account_service.get_account(ton_address=token_account_address)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found!")

    return account


# === === === === === === ===
