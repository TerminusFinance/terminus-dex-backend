from src.database.repositories.event_repo import EventRepository
from src.utils.logging import create_custom_logger, log_error

from .base_service import BaseService

logger = create_custom_logger("EventService")


class EventService(BaseService):

    # === === === === === === ===
    @log_error(logger)
    async def save_login_event(
        self,
        account_id: int,
    ) -> None:

        event_repo = EventRepository(session=self.session)
        await event_repo.save_login_event(account_id=account_id)

    # === === === === === === ===
    @log_error(logger)
    async def save_new_referral_event(
        self,
        account_id: int,
        referral_account_id: int,
    ) -> None:

        event_repo = EventRepository(session=self.session)
        await event_repo.save_new_referral_event(
            account_id=account_id,
            referral_account_id=referral_account_id,
        )
