from pydantic import BaseModel


class BlockShardInfo(BaseModel):
    last_known_block_id: str | None = None
    error: str | None = None
