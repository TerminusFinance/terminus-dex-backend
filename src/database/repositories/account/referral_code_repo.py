from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database_models.account.referral_code import ReferralCodeType

from ...database_models.account import ReferralCodeDb

# === === === === === === ===


class ReferralCodeRepository:

    # === === === === === === ===

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.session = session

    # === === === === === === ===

    async def create(
        self,
        account_id: int,
        code: str,
        type: ReferralCodeType = ReferralCodeType.DEFAULT,
        needs_flush: bool = False,
    ) -> ReferralCodeDb:

        referral_code = ReferralCodeDb(
            account_id=account_id,
            code=code,
            type=type,
        )

        self.session.add(referral_code)
        if needs_flush:
            await self.session.flush()

        return referral_code

    # === === === === === === ===

    async def is_exists(
        self,
        code: str,
    ) -> bool:

        query = select(ReferralCodeDb).where(ReferralCodeDb.code == code)
        result = await self.session.execute(query)

        return bool(result.unique().scalar_one_or_none())

    # === === === === === === ===

    async def get(
        self,
        code: str,
    ) -> ReferralCodeDb | None:

        query = select(ReferralCodeDb).where(ReferralCodeDb.code == code)
        result = await self.session.execute(query)

        return result.unique().scalar_one_or_none()

    # === === === === === === ===
