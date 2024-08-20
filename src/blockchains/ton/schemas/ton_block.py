from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TonBlock(BaseModel):

    workchain: int
    shard: str
    seqno: int
    is_processed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def block_id(self) -> str:
        return f"({self.workchain},{self.shard},{self.seqno})"

    def __str__(self) -> str:
        return self.block_id

    @staticmethod
    def from_string(block_id: str) -> "TonBlock":
        workchain_id, shard, seqno = block_id[1:-1].split(",")

        return TonBlock(
            workchain=int(workchain_id),
            shard=shard,
            seqno=int(seqno),
        )
