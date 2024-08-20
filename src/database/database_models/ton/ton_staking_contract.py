from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.database_models.mixins.created_at_mixin import CreatedAtMixin
from src.database.database_models.mixins.id_mixin import IdMixin
from src.database.database_models.mixins.modified_at_mixin import ModifiedAtMixin
from src.database.database_models.mixins.soft_deletable_mixin import SoftDeletableMixin

from ..base import Base

if TYPE_CHECKING:
    from .ton_dex_asset import TonAssetDb


class TonStakingContractDb(
    Base,
    IdMixin,
    CreatedAtMixin,
    ModifiedAtMixin,
    SoftDeletableMixin,
):

    __tablename__ = "ton_staking_contract"

    # === === === Columns === === ===
    address: Mapped[str] = mapped_column(String(48), nullable=False, unique=True)
    in_asset_address: Mapped[str] = mapped_column(
        String(48), ForeignKey("ton_asset.address"), nullable=False
    )
    out_asset_address: Mapped[str] = mapped_column(
        String(48), ForeignKey("ton_asset.address"), nullable=False
    )
    apy: Mapped[float] = mapped_column(Float, nullable=False)
    min_offer_amount: Mapped[int] = mapped_column(Float, nullable=False)
    fees: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    # === === === Relationships === === ===
    in_asset: Mapped["TonAssetDb"] = relationship(lazy="joined", foreign_keys=[in_asset_address])
    out_asset: Mapped["TonAssetDb"] = relationship(lazy="joined", foreign_keys=[out_asset_address])
