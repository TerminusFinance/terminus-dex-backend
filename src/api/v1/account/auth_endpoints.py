import logging
from typing import Annotated

from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.constants.api_message_code import ApiMessageCode
from src.dependencies import get_config, get_session
from src.dependencies.ton_client import get_ton_client
from src.exceptions.payload_exceptions import PayloadExpiredError, PayloadNotFoundError
from src.exceptions.tonproof_exceptions import (
    GettingPublicKeyError,
    PublicKeysMismatchError,
    SignatureVerificationError,
    TonProofExpiredError,
)
from src.models.account import Account
from src.services import AuthService, PayloadService
from src.services.account_service import AccountService
from src.services.event_service import EventService

from ..schemas.account import AuthRequest
from ..schemas.base_messages import ErrorMessage, Message, SuccessMessage

logger = logging.getLogger("AuthEndpoints")


# === === === === === === ===


async def auth(
    request_body: AuthRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
    ton_client: Annotated[TonClient, Depends(get_ton_client)],
) -> Message:

    # Checking payload
    payload_service = PayloadService(session=session, config=config)
    try:
        await payload_service.is_payload_valid(payload=request_body.proof.payload)
    except PayloadNotFoundError:
        return ErrorMessage(code=ApiMessageCode.PAYLOAD_NOT_FOUND, error="Payload not found.")
    except PayloadExpiredError:
        return ErrorMessage(code=ApiMessageCode.PAYLOAD_EXPIRED, error="Payload expired.")
    # === === ===

    # Checking ton proof
    auth_service = AuthService(config=config)
    try:
        await auth_service.check_ton_proof(
            wallet_address=request_body.address,
            ton_proof=request_body.proof,
            ton_client=ton_client,
        )
    except TonProofExpiredError:
        return ErrorMessage(
            code=ApiMessageCode.TON_PROOF_EXPIRED,
            error="Ton proof expired.",
        )
    except GettingPublicKeyError:
        return ErrorMessage(
            code=ApiMessageCode.TON_PROOF_GETTING_PUBLIC_KEY_FAILED,
            error="Failed to get public key.",
        )
    except PublicKeysMismatchError:
        return ErrorMessage(
            code=ApiMessageCode.TON_PROOF_PUBLIC_KEYS_MISMATCH,
            error="Public keys mismatch.",
        )
    except SignatureVerificationError:
        return ErrorMessage(
            code=ApiMessageCode.TON_PROOF_SIGNATURE_VERIFICATION_FAILED,
            error="Signature verification failed.",
        )
    # === === ===

    # Signing token
    token, token_payload = auth_service.sign_new_token(
        wallet_address=request_body.address.to_string()
    )
    auth_service.set_cookies_to_response(
        response=response, token=token, token_payload=token_payload
    )
    # === === ===

    affiliate_account: Account | None = None

    # Saving account if not exists
    account_service = AccountService(session=session, config=config)
    account = await account_service.get_account(ton_address=request_body.address)
    if not account:
        if request_body.referral_code:
            affiliate_account = await account_service.get_account_by_referral_code(
                code=request_body.referral_code
            )

        account = await account_service.create_new_account(
            ton_address=request_body.address,
            affiliate_ton_address=affiliate_account.ton_address if affiliate_account else None,
            needs_flush=True,
        )

    await session.commit()
    # === === ===

    # Saving events
    try:
        event_service = EventService(session=session, config=config)
        await event_service.save_login_event(account_id=account.id)
        if affiliate_account:
            await event_service.save_new_referral_event(
                account_id=affiliate_account.id, referral_account_id=account.id
            )
        await session.commit()
    except Exception:
        logger.exception("Failed to save login event.")
        await session.rollback()
    # === === ===

    return SuccessMessage()


# === === === === === === ===
