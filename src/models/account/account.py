from pydantic import BaseModel
from src.database.database_models.account.account import AccountDb
from src.types.ton.ton_address_annotated import TonAddressType
from src.utils.ton_address import TonAddress


class Account(BaseModel):

    id: int
    ton_address: TonAddressType
    affiliate_ton_address: TonAddressType | None

    # === === === === === === ===

    @staticmethod
    def from_db_model(account_db: AccountDb) -> "Account":

        return Account(
            id=account_db.id,
            ton_address=TonAddress(account_db.ton_address),
            affiliate_ton_address=(
                TonAddress(account_db.affiliate_ton_address)
                if account_db.affiliate_ton_address
                else None
            ),
        )

    # === === === === === === ===
