from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.database_models.mixins.created_at_mixin import CreatedAtMixin
from src.database.database_models.mixins.id_mixin import IdMixin
from src.database.database_models.mixins.modified_at_mixin import ModifiedAtMixin
from src.database.database_models.mixins.soft_deletable_mixin import SoftDeletableMixin

from ..base import Base

if TYPE_CHECKING:
    from .ton_dex_asset import TonAssetDb


# === === === === === === ===


class TonDexPoolDb(
    Base,
    IdMixin,
    CreatedAtMixin,
    ModifiedAtMixin,
    SoftDeletableMixin,
):

    __tablename__ = "ton_dex_pool"

    # === === === Columns === === ===
    address: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    reserve_0: Mapped[int] = mapped_column(Numeric(asdecimal=False), nullable=False)
    reserve_1: Mapped[int] = mapped_column(Numeric(asdecimal=False), nullable=False)
    token_0_minter_address: Mapped[str] = mapped_column(
        String(100), ForeignKey("ton_asset.address"), nullable=False
    )
    token_1_minter_address: Mapped[str] = mapped_column(
        String(100), ForeignKey("ton_asset.address"), nullable=False
    )
    token_0_wallet_address: Mapped[str] = mapped_column(String(100), nullable=False)
    token_1_wallet_address: Mapped[str] = mapped_column(String(100), nullable=False)
    lp_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    ref_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol_fee_address: Mapped[str] = mapped_column(String(100), nullable=False)
    collected_token_0_protocol_fee: Mapped[int] = mapped_column(
        Numeric(asdecimal=False), nullable=False
    )
    collected_token_1_protocol_fee: Mapped[int] = mapped_column(
        Numeric(asdecimal=False), nullable=False
    )

    total_supply: Mapped[int] = mapped_column(Numeric(asdecimal=False), nullable=False)

    # === === === Relationships === === ===

    asset_0: Mapped["TonAssetDb"] = relationship(
        lazy="joined", foreign_keys=[token_0_minter_address]
    )
    asset_1: Mapped["TonAssetDb"] = relationship(
        lazy="joined", foreign_keys=[token_1_minter_address]
    )
