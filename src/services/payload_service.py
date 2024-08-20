import logging
from datetime import UTC, datetime, timedelta

from nacl.utils import random
from src.database.repositories.payload_repo import PayloadRepository
from src.exceptions import PayloadCreationError, PayloadExpiredError, PayloadNotFoundError

from .base_service import BaseService

logger = logging.getLogger("PayloadService")


class PayloadService(BaseService):

    # === === === === === === ===
    async def create_payload(
        self,
        needs_flush: bool = False,
        lifetime_in_minutes: int | None = None,
    ) -> str:

        if not lifetime_in_minutes:
            lifetime_in_minutes = self.config.account.payload_lifetime_minutes
        expired_at = datetime.now(UTC) + timedelta(minutes=lifetime_in_minutes)

        payload_repo = PayloadRepository(session=self.session)

        attempts = 0
        while attempts < self.config.account.payload_creating_max_tries:
            payload = bytearray(random(8))

            ts = int(expired_at.timestamp())
            payload.extend(ts.to_bytes(8, byteorder="big"))

            payload_db = await payload_repo.save_payload(
                payload=payload.hex(), expired_at=expired_at, needs_flush=needs_flush
            )
            if payload_db:
                break
            attempts += 1

        if not payload_db:
            logger.error("Failed to create payload.")
            raise PayloadCreationError("Failed to create payload.")

        return payload_db.payload

    # === === === === === === ===
    async def is_payload_valid(
        self,
        payload: str,
    ) -> bool:

        payload_repo = PayloadRepository(session=self.session)
        payload_db = await payload_repo.get_payload(payload=payload)

        if not payload_db:
            raise PayloadNotFoundError(f"Payload {payload} not found.")

        if payload_db.expired_at < datetime.now(UTC):
            raise PayloadExpiredError(f"Payload {payload} expired.")

        return True
