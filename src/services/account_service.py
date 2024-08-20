import random
import string

from src.database.repositories.account.account_repo import AccountRepository
from src.database.repositories.account.referral_code_repo import ReferralCodeRepository
from src.models.account import Account
from src.utils.ton_address import TonAddress

from .base_service import BaseService


class AccountService(BaseService):

    # === === === === === === ===

    async def create_new_account(
        self,
        ton_address: TonAddress,
        affiliate_ton_address: TonAddress | None = None,
        needs_flush: bool = False,
    ) -> Account:

        referral_str_address = affiliate_ton_address.str_address if affiliate_ton_address else None

        account_repo = AccountRepository(session=self.session)
        account_db = await account_repo.create(
            ton_address=ton_address.str_address,
            affiliate_ton_address=referral_str_address,
            needs_flush=needs_flush,
        )

        referral_code_repo = ReferralCodeRepository(session=self.session)
        referral_code = await self._create_referral_code(referral_code_repo=referral_code_repo)

        await referral_code_repo.create(
            account_id=account_db.id,
            code=referral_code,
        )

        account = Account.from_db_model(account_db=account_db)

        return account

    # === === === === === === ===

    async def get_account(
        self,
        account_id: int | None = None,
        ton_address: TonAddress | None = None,
    ) -> Account | None:

        ton_address_str = ton_address.str_address if ton_address else None

        account_repo = AccountRepository(session=self.session)
        account_db = await account_repo.get(id=account_id, ton_address=ton_address_str)

        if account_db:
            account = Account.from_db_model(account_db=account_db)
            return account

        return None

    # === === === === === === ===

    async def get_account_by_referral_code(
        self,
        code: str,
    ) -> Account | None:

        referral_code_repo = ReferralCodeRepository(session=self.session)
        referral_code = await referral_code_repo.get(code=code)

        if referral_code:
            return Account.from_db_model(referral_code.account)

        return None

    # === === === === === === ===

    async def _create_referral_code(
        self,
        referral_code_repo: ReferralCodeRepository,
    ) -> str:
        """Generate a new referral code.

        Args:
            referral_code_repo (ReferralCodeRepository): The repository to use for checking code
                existence.

        Returns:
            str: A newly generated referral code.

        Raises:
            Exception: If five attempts to generate a new referral code fail.
        """

        attempts = 0
        while attempts < 5:
            code = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits, k=self.config.app.referral_code_length
                )
            )

            if not await referral_code_repo.is_exists(code=code):
                return code

            attempts += 1

        raise Exception("Failed to create referral code.")

    # === === === === === === ===
