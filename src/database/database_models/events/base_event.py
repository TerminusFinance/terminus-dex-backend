from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from ..mixins import CreatedAtMixin, IdMixin


class BaseEventDb(
    AbstractConcreteBase,
    Base,
    IdMixin,
    CreatedAtMixin,
):

    strict_attrs = True

    # === === === Columns === === ===
    account_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("account.id"), nullable=False)
