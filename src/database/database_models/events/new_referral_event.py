from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_event import BaseEventDb


class NewReferralEventDb(BaseEventDb):

    __tablename__ = "new_referral_event"

    # === === === Columns === === ===
    referral_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("account.id"), nullable=False)

    # === === === Args === === ===
    __mapper_args__ = {
        "polymorphic_identity": "new_referral",
        "concrete": True,
    }
