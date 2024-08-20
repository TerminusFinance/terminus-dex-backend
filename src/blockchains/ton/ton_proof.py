import hashlib
import logging
from datetime import UTC, datetime, timedelta

from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from pytoniq_core.boc import Cell
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.wallet_versions import WalletVersion, get_wallet_version
from src.exceptions.tonproof_exceptions import (
    GettingPublicKeyError,
    PublicKeysMismatchError,
    SignatureVerificationError,
    TonProofExpiredError,
)
from src.types.ton_proof import TonProof
from src.utils.str_tools import b64str_to_bytes, bytes_to_b64str
from src.utils.ton_address import TonAddress

logger = logging.getLogger(__name__)


# === === === === === === ===
async def check_ton_proof(
    wallet_address: TonAddress,
    ton_proof: TonProof,
    ton_client: TonClient | None = None,
) -> bool:

    if datetime.now(UTC) - datetime.fromtimestamp(ton_proof.timestamp, UTC) > timedelta(minutes=5):
        logger.debug("Payload expired. Wallet: %s", wallet_address.to_string())
        raise TonProofExpiredError("Ton proof expired.")

    public_key = None

    if ton_proof.state_init:
        public_key = await get_public_key_from_state_init(state_init=ton_proof.state_init)

    if ton_client and not public_key:
        public_key = await get_public_key_from_remote_api(
            wallet_address=wallet_address, state_init=ton_proof.state_init, ton_client=ton_client
        )

    if not public_key:
        logger.debug("Failed to get public key. Wallet: %s", wallet_address.to_string())
        raise GettingPublicKeyError("Failed to get public key")

    if ton_proof.public_key and ton_proof.public_key != public_key:
        logger.debug("Public keys mismatch. Wallet: %s", wallet_address.to_string())
        raise PublicKeysMismatchError("Public keys mismatch")

    signature_message = prepare_message(wallet_address=wallet_address, ton_proof=ton_proof)
    try:
        verify_public_key(
            public_key=public_key,
            signature_message=signature_message,
            signature=ton_proof.signature,
            address=wallet_address,
        )
        return True
    except BadSignatureError:
        logger.debug("Signature verification failed. Wallet: %s", wallet_address.to_string())
        raise SignatureVerificationError("Signature verification failed.")


# === === === === === === ===
def prepare_message(
    wallet_address: TonAddress,
    ton_proof: TonProof,
) -> bytearray:

    message = bytearray()
    message.extend("ton-proof-item-v2/".encode())
    message.extend(wallet_address.wc.to_bytes(4, "little"))
    message.extend(wallet_address.hash_part)
    message.extend(ton_proof.domain.length_bytes.to_bytes(4, "little"))
    message.extend(ton_proof.domain.value.encode())
    message.extend(ton_proof.timestamp.to_bytes(8, "little"))
    message.extend(ton_proof.payload.encode())

    signature_message = bytearray()
    signature_message.extend(bytes.fromhex("ffff"))
    signature_message.extend("ton-connect".encode())
    signature_message.extend(hashlib.sha256(message).digest())

    return signature_message


# === === === === === === ===
async def get_public_key_from_state_init(
    state_init: str,
):

    try:
        cell = Cell.one_from_boc(b64str_to_bytes(state_init))
        state_init_slice = cell.begin_parse()

        state_init_slice.skip_bits(2)
        code_cell = state_init_slice.load_maybe_ref()
        if not code_cell:
            return None

        data_cell = state_init_slice.load_maybe_ref()

        if not data_cell:
            return None

        code_cell_hash = bytes_to_b64str(code_cell.hash)

        wallet_version = get_wallet_version(wallet_code_cell_hash=code_cell_hash)

        if not wallet_version:
            return None

        public_key = _get_public_key_from_data(data_cell=data_cell, wallet_version=wallet_version)

        return public_key
    except Exception:
        logger.debug("Failed to get public key from state init.")
        return None


# === === === === === === ===
def _get_public_key_from_data(
    data_cell: Cell,
    wallet_version: WalletVersion,
) -> str | None:
    data_slice = data_cell.begin_parse()

    if wallet_version in {
        WalletVersion.V2R1,
        WalletVersion.V2R2,
    }:
        data_slice.skip_bits(32)
    elif wallet_version in {
        WalletVersion.V3R1,
        WalletVersion.V3R2,
        WalletVersion.V4R1,
        WalletVersion.V4R2,
    }:
        data_slice.skip_bits(64)
    elif wallet_version == WalletVersion.V5:
        data_slice.skip_bits(65)
    elif wallet_version == WalletVersion.HV2:
        data_slice.skip_bits(32)
    elif wallet_version == WalletVersion.HV3:
        pass
    else:
        return None

    public_key_bytes = data_slice.load_bytes(32)

    return public_key_bytes.hex()


# === === === === === === ===
def verify_public_key(
    public_key: str,
    signature_message: bytes,
    signature: str,
    address: TonAddress,
):

    try:
        verify_key = VerifyKey(public_key.encode(), HexEncoder)
        verify_key.verify(
            hashlib.sha256(signature_message).digest(),
            b64str_to_bytes(signature),
        )
        return True
    except BadSignatureError:
        logger.debug("Failed to verify signature for wallet %s", address.to_string())
        return False


# === === === === === === ===
async def get_public_key_from_remote_api(
    wallet_address: TonAddress,
    ton_client: TonClient,
    state_init: str | None = None,
) -> str | None:

    public_key = None
    try:
        public_key = await ton_client.get_public_key(wallet_address=wallet_address)
    except Exception:
        pass

    try:
        if not public_key and state_init:
            public_key = await ton_client.get_public_key_from_state_init(state_init=state_init)
    except Exception:
        pass

    if not public_key:
        logger.debug(
            "Failed to get public key from remote API. Wallet: %s", wallet_address.to_string()
        )

    return public_key
