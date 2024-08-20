from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.database_models.mixins.created_at_mixin import CreatedAtMixin
from src.database.database_models.mixins.id_mixin import IdMixin
from src.database.database_models.mixins.modified_at_mixin import ModifiedAtMixin

from ..base import Base

if TYPE_CHECKING:
    from .referral_code import ReferralCodeDb


class AccountDb(
    Base,
    IdMixin,
    CreatedAtMixin,
    ModifiedAtMixin,
):

    __tablename__ = "account"

    # === === === Columns === === ===
    ton_address: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    affiliate_ton_address: Mapped[str] = mapped_column(String(50), nullable=True)

    # === === === Relations === === ===
    referral_codes: Mapped[List["ReferralCodeDb"]] = relationship(lazy="joined")
