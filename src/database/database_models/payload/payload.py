from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from ..mixins import CreatedAtMixin


class PayloadDb(
    Base,
    CreatedAtMixin,
):

    __tablename__ = "payload"

    # === === === Columns === === ===
    payload: Mapped[str] = mapped_column(String, primary_key=True, nullable=False, unique=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
