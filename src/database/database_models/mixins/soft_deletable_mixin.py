from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeletableMixin:

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleting_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
