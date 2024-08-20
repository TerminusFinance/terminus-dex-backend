from fastapi import APIRouter
from src.api.v1.schemas.base_messages import ErrorMessage, SuccessMessage
from src.api.v1.schemas.payload import PayloadResponse
from src.blockchains.ton.schemas.balances import Balances

from .account_endpoints import get_balances
from .auth_endpoints import auth
from .payload_endpoints import get_tonproof_payload

# === === === === === === ===

account_router = APIRouter(
    include_in_schema=True,
)

# === === === === === === ===

account_router.add_api_route(
    path="/get_payload",
    endpoint=get_tonproof_payload,
    methods=["GET"],
    response_model=PayloadResponse | ErrorMessage,
)

# === === === === === === ===

account_router.add_api_route(
    path="/auth",
    endpoint=auth,
    methods=["POST"],
    response_model=SuccessMessage | ErrorMessage,
)

# === === === === === === ===

account_router.add_api_route(
    path="/{account_address}/balances",
    endpoint=get_balances,
    methods=["GET"],
    response_model=Balances | ErrorMessage,
)

# === === === === === === ===
