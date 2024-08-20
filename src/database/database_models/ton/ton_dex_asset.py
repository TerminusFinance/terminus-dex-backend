from sqlalchemy import Boolean, ForeignKey, Integer, String, sql
from sqlalchemy.orm import Mapped, mapped_column
from src.database.database_models.mixins.created_at_mixin import CreatedAtMixin
from src.database.database_models.mixins.id_mixin import IdMixin
from src.database.database_models.mixins.modified_at_mixin import ModifiedAtMixin
from src.database.database_models.mixins.soft_deletable_mixin import SoftDeletableMixin

from ..base import Base


class TonAssetDb(
    Base,
    IdMixin,
    CreatedAtMixin,
    ModifiedAtMixin,
    SoftDeletableMixin,
):

    __tablename__ = "ton_asset"

    # === === === Columns === === ===
    address: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    decimals: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(), nullable=True)

    is_whitelisted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=sql.false(), default=False
    )
    is_community: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deprecated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    account_address: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("account.ton_address"),
        nullable=True,
        server_default=None,
        default=None,
    )

    # === === === Relationships === === ===
    # account: Mapped["AccountDb"] = relationship(foreign_keys=[account_address])
