# === === === === === === ===

from typing import Literal

from sqlalchemy import select
from src.database.repositories.base_repo import BaseRepository

from ..database_models.storage import StorageCellDb

# === === === === === === ===


class StorageCellRepo(BaseRepository):

    # === === === === === === ===

    async def get(
        self,
        key: str,
    ) -> StorageCellDb | None:

        query = select(StorageCellDb).where(StorageCellDb.key == key)
        result = await self.session.execute(query)
        cell = result.scalar_one_or_none()
        return cell

    # === === === === === === ===

    async def get_value(
        self,
        key: str,
        type: Literal["int", "str"],
    ) -> int | str | None:

        cell = await self.get(key=key)
        if not cell:
            return None
        if type == "int":
            return cell.value
        if type == "str":
            return cell.value_str

    # === === === === === === ===

    async def set(
        self,
        key: str,
        value: int | None = None,
        value_str: str | None = None,
        needs_flush: bool = False,
    ) -> StorageCellDb:

        element = await self.get(key=key)

        if not element:
            element = StorageCellDb(key=key)

        element.value = value
        element.value_str = value_str

        self.session.add(element)
        if needs_flush:
            await self.session.flush()

        return element

    # === === === === === === ===
