import logging
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from ..database_models.payload import PayloadDb
from .base_repo import BaseRepository

logger = logging.getLogger("PayloadRepository")


class PayloadRepository(BaseRepository):

    # === === === === === === ===
    async def save_payload(
        self,
        payload: str,
        expired_at: datetime,
        needs_flush: bool = False,
    ) -> PayloadDb | None:

        payload_db = PayloadDb(payload=payload, expired_at=expired_at)
        try:
            self.session.add(payload_db)
            if needs_flush:
                await self.session.flush()
        except IntegrityError as e:
            logger.warning(f"Payload integrity Error. Payload: {payload}. Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to save payload. Payload: {payload}. Error: {e}")
            return None

        return payload_db

    # === === === === === === ===
    async def get_payload(
        self,
        payload: str,
    ) -> PayloadDb | None:

        payload_db = await self.session.get(PayloadDb, payload)
        return payload_db
