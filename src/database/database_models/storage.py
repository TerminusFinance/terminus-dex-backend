# === === === === === === ===

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from src.database.database_models.mixins.created_at_mixin import CreatedAtMixin
from src.database.database_models.mixins.id_mixin import IdMixin

from .base import Base

# === === === === === === ===


class StorageCellDb(
    Base,
    CreatedAtMixin,
    IdMixin,
):

    __tablename__ = "storage_cell"

    # === === === === === === ===

    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None)
    value_str: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)


# === === === === === === ===
