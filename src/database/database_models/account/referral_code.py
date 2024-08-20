from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.database_models.mixins.created_at_mixin import CreatedAtMixin
from src.database.database_models.mixins.id_mixin import IdMixin
from src.database.database_models.mixins.soft_deletable_mixin import SoftDeletableMixin

from ..base import Base

if TYPE_CHECKING:
    from .account import AccountDb

# === === === === === === ===


class ReferralCodeType(IntEnum):
    DEFAULT = 0
    CUSTOM = 1


# === === === === === === ===


class ReferralCodeDb(
    Base,
    IdMixin,
    CreatedAtMixin,
    SoftDeletableMixin,
):

    __tablename__ = "referral_code"

    # === === === Columns === === ===
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("account.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    type: Mapped[ReferralCodeType] = mapped_column(
        Integer, nullable=False, default=ReferralCodeType.DEFAULT, server_default="0"
    )

    # === === === Relationships === === ===
    account: Mapped["AccountDb"] = relationship(back_populates="referral_codes", lazy="joined")
