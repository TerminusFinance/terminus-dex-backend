from pytonapi.schema.blockchain import (
    BlockchainBlock,
    MethodExecutionResult,
    Transaction,
    TvmStackRecord,
)
from pytonapi.schema.jettons import JettonInfo
from pytonapi.schema.traces import Message
from src.blockchains.ton.schemas.get_method_result import GetMethodResult, StackRecord
from src.blockchains.ton.schemas.ton_jetton_info import TonJettonInfo
from src.utils.ton_address import TonAddress

from ...schemas import TonBlock, TonMessage, TonTransaction

# === === === === === === ===


class BlockMapper:

    @staticmethod
    def to_model(block: BlockchainBlock) -> TonBlock:

        return TonBlock(
            workchain=block.workchain_id,
            shard=block.shard,
            seqno=block.seqno,
        )


# === === === === === === ===


class MessageMapper:

    @staticmethod
    def to_model(message: Message) -> TonMessage:

        return TonMessage(
            created_lt=message.created_lt,
            value=message.value,
            destination=(
                TonAddress(message.destination.address.to_userfriendly())
                if message.destination
                else None
            ),
            source=(
                TonAddress(message.source.address.to_userfriendly()) if message.source else None
            ),
            op_code=message.op_code,  # type: ignore  # pydantic validator
            decoded_op_name=message.decoded_op_name,
            decoded_body=message.decoded_body,
            raw_body=message.raw_body,
        )


# === === === === === === ===


class TransactionMapper:

    @staticmethod
    def to_model(transaction: Transaction) -> TonTransaction:
        return TonTransaction(
            block_id=transaction.block,
            hash=transaction.hash,
            lt=transaction.lt,
            account=TonAddress(transaction.account.address.to_userfriendly()),
            utime=transaction.utime,
            in_msg=MessageMapper().to_model(transaction.in_msg) if transaction.in_msg else None,
            out_msgs=[MessageMapper().to_model(out_msg) for out_msg in transaction.out_msgs],
        )


# === === === === === === ===


class StackRecordMapper:

    @staticmethod
    def to_model(record_raw: TvmStackRecord) -> StackRecord:

        record = StackRecord(
            type=record_raw.type,
            cell=record_raw.cell,
            slice=record_raw.slice,
            num=record_raw.num,
            tuple=(
                [StackRecordMapper.to_model(subrecord) for subrecord in record_raw.tuple]
                if record_raw.tuple
                else None
            ),
        )

        return record


# === === === === === === ===


class GetMethodResultMapper:

    @staticmethod
    def to_model(result_raw: MethodExecutionResult) -> GetMethodResult:

        return GetMethodResult(
            success=result_raw.success,
            exit_code=result_raw.exit_code,
            stack=[StackRecordMapper.to_model(record) for record in result_raw.stack],
            decoded=result_raw.decoded,
        )


# === === === === === === ===


class JettonInfoMapper:

    @staticmethod
    def to_model(jetton_info_raw: JettonInfo) -> TonJettonInfo:

        return TonJettonInfo(
            address=TonAddress(jetton_info_raw.metadata.address.to_userfriendly()),
            name=jetton_info_raw.metadata.name,
            symbol=jetton_info_raw.metadata.symbol,
            decimals=int(jetton_info_raw.metadata.decimals),
            image_url=jetton_info_raw.metadata.image,
            is_whitelisted=jetton_info_raw.verification == "whitelist",
            is_community=jetton_info_raw.verification == "none",
            is_blacklisted=jetton_info_raw.verification == "blacklist",
        )


# === === === === === === ===
