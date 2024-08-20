from typing import List

from sqlalchemy import select
from src.database.database_models.events.base_event import BaseEventDb
from src.database.database_models.events.login_event import LoginEventDb
from src.database.database_models.events.new_referral_event import NewReferralEventDb

from .base_repo import BaseRepository


class EventRepository(BaseRepository):

    # === === === === === === ===
    async def get_account_events(
        self,
        account_id: int,
    ) -> List[BaseEventDb]:

        query = select(BaseEventDb).where(BaseEventDb.account_id == account_id)
        result = await self.session.execute(query)
        events_sequence = result.unique().scalars().all()

        return list(events_sequence)

    # === === === Login event methods === === ===
    async def save_login_event(
        self,
        account_id: int,
        needs_flush: bool = False,
    ) -> LoginEventDb:

        login_event = LoginEventDb(account_id=account_id)
        self.session.add(login_event)

        if needs_flush:
            await self.session.flush()

        return login_event

    # === === === === === === ===
    async def get_account_login_events(
        self,
        account_id: int,
    ) -> List[LoginEventDb]:

        query = select(LoginEventDb).where(LoginEventDb.account_id == account_id)
        result = await self.session.execute(query)
        events_sequence = result.unique().scalars().all()

        return list(events_sequence)

    # === === === New referral event methods === === ===
    async def save_new_referral_event(
        self,
        account_id: int,
        referral_account_id: int,
        needs_flush: bool = False,
    ) -> None:

        new_referral_event = NewReferralEventDb(
            account_id=account_id,
            referral_id=referral_account_id,
        )
        self.session.add(new_referral_event)

        if needs_flush:
            await self.session.flush()
