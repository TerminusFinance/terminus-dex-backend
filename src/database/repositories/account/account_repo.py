import logging

from sqlalchemy import select

from ...database_models.account import AccountDb
from ..base_repo import BaseRepository

# === === === === === === ===

logger = logging.getLogger("AccountRepository")


# === === === === === === ===


class AccountRepository(BaseRepository):

    # === === === === === === ===

    async def create(
        self,
        ton_address: str,
        affiliate_ton_address: str | None = None,
        needs_flush: bool = False,
    ) -> AccountDb:

        account = AccountDb(ton_address=ton_address, affiliate_ton_address=affiliate_ton_address)
        self.session.add(account)

        if needs_flush:
            await self.session.flush()

        return account

    # === === === === === === ===

    async def get(
        self,
        id: int | None = None,
        ton_address: str | None = None,
    ) -> AccountDb | None:

        if id is not None:
            account = await self.session.get(AccountDb, id)

        if ton_address is not None:
            query = select(AccountDb).where(AccountDb.ton_address == ton_address)
            result = await self.session.execute(query)
            account = result.unique().scalar_one_or_none()

        return account

    # === === === === === === ===
