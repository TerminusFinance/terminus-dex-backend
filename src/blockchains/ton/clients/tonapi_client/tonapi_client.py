from collections import defaultdict
from typing import Dict, List

from pytonapi import AsyncTonapi
from pytonapi.exceptions import TONAPINotFoundError
from src.blockchains.ton.clients.exceptions import TonGetMethodNotFoundError
from src.blockchains.ton.schemas.ton_transaction import TonTransaction
from src.config import Config
from src.utils.ton_address import TonAddress

from ...schemas.balances import Balances
from ...schemas.get_method_result import GetMethodResult
from ...schemas.ton_jetton_info import TonJettonInfo
from ..ton_client import TonClient
from ..utils import get_address_cell, parse_address_from_bytes
from .mappers import GetMethodResultMapper, JettonInfoMapper, TransactionMapper


class TonApiClient(TonClient):

    jetton_wallets_cache: Dict[TonAddress, Dict[TonAddress, TonAddress]] = defaultdict(lambda: {})

    # === === === === === ===

    def __init__(
        self,
        config: Config,
    ) -> None:

        # self.jetton_wallets_cache: Dict[TonAddress, Dict[TonAddress, TonAddress]] = defaultdict(
        #     lambda: {}
        # )
        self.tonapi = AsyncTonapi(
            api_key=config.ton_console.api_key.get_secret_value(),
            is_testnet=config.ton_console.is_testnet,
            max_retries=config.ton_console.max_retries,
        )

    # === === === === === === ===

    async def _get_wallet_from_cache(
        self,
        owner_address: TonAddress,
        jetton_minter_address: TonAddress,
    ) -> TonAddress | None:

        if (
            owner_address in TonApiClient.jetton_wallets_cache
            and jetton_minter_address in TonApiClient.jetton_wallets_cache[owner_address]
        ):
            return TonApiClient.jetton_wallets_cache[owner_address][jetton_minter_address]

        return None

    # === === === === === === ===

    async def _save_wallet_to_cache(
        self,
        owner_address: TonAddress,
        jetton_minter_address: TonAddress,
        jetton_wallet_address: TonAddress,
    ) -> None:

        TonApiClient.jetton_wallets_cache[owner_address][
            jetton_minter_address
        ] = jetton_wallet_address

    # === === === === === ===

    async def run_get_method(
        self,
        address: TonAddress,
        method_name: str,
        *args: str | None,
    ) -> GetMethodResult:

        try:
            raw_result = await self.tonapi.blockchain.execute_get_method(
                address.to_string(),
                method_name,
                *args,
            )
        except TONAPINotFoundError:
            raise TonGetMethodNotFoundError("Method not found. Maybe contract is not deployed.")

        result = GetMethodResultMapper.to_model(raw_result)

        return result

    # === === === === === ===

    # async def get_last_masterchain_block(
    #     self,
    # ) -> TonBlock:

    #     block = await self.tonapi.blockchain.get_last_masterchain_block()

    #     return BlockMapper().to_model(block=block)

    # # === === === === ===
    # async def get_masterchain_block_shards(
    #     self,
    #     masterchain_block: TonBlock,
    # ) -> List[TonBlock]:

    #     block_shards = await self.tonapi.blockchain.get_block(
    #         masterchain_seqno=masterchain_block.seqno
    #     )

    #     blocks = []

    #     for block_shard in block_shards.shards:
    #         shard_info = BlockShardInfo.model_validate(block_shard)
    #         if shard_info.error:
    #             raise Exception(f"Error: {shard_info.error}. Shard info: {shard_info}")
    #         if not shard_info.last_known_block_id:
    #             continue
    #         blocks.append(TonBlock.from_string(shard_info.last_known_block_id))

    #     return blocks

    # # === === === === ===
    # async def get_block_transactions(
    #     self,
    #     block: TonBlock,
    # ) -> List[TonTransaction]:

    #     transactions = await self.tonapi.blockchain.get_transaction_from_block(
    #         block_id=block.block_id
    #     )

    #     return [
    #         TransactionMapper().to_model(transaction=transaction)
    #         for transaction in transactions.transactions
    #     ]

    # # === === === === ===
    # async def get_jetton_wallet_data(
    #     self,
    #     jetton_wallet_address: TonAddress,
    # ) -> JettonWalletData:

    #     response = await self.tonapi.blockchain.execute_get_method(
    #         str(jetton_wallet_address),
    #         "get_wallet_data",
    #     )

    #     if (
    #         not response.stack
    #         or len(response.stack) < 4
    #         or not response.stack[0].num
    #         or not response.stack[1].cell
    #         or not response.stack[2].cell
    #     ):
    #         raise Exception("Failed to get jetton wallet data")

    #     balance = int(response.stack[0].num, 16)
    #     owner_wallet_address = parse_address_from_bytes(bytes.fromhex(response.stack[1].cell))
    #     jetton_contract_address = parse_address_from_bytes(bytes.fromhex(response.stack[2].cell))

    #     if not jetton_contract_address or not owner_wallet_address:
    #         raise Exception("Failed to get jetton wallet data")

    #     return JettonWalletData(
    #         jetton_wallet_address=TonAddress(jetton_wallet_address),
    #         balance=balance,
    #         jetton_contract_address=TonAddress(jetton_contract_address),
    #         owner_wallet_address=TonAddress(owner_wallet_address),
    #     )

    # # === === === === ===
    # async def send_message(
    #     self,
    #     message_boc: str,
    # ) -> bool:

    #     return await self.tonapi.blockchain.send_message(body={"boc": message_boc})

    # === === === === === ===

    async def get_jetton_wallet_address(
        self,
        jetton_minter_address: TonAddress,
        owner_address: TonAddress,
    ) -> TonAddress | None:
        """Get jetton wallet address.

        Args:
            jetton_contract_address (TonAddress): Jetton contract address.
            owner_wallet_address (TonAddress): Owner wallet address.

        Returns:
            TonAddress | None: Jetton wallet address or None if not found.
        """

        wallet_address = await self._get_wallet_from_cache(
            owner_address=owner_address,
            jetton_minter_address=jetton_minter_address,
        )

        if wallet_address:
            return wallet_address

        owner_wallet_address_cell = get_address_cell(owner_address._address)

        response = await self.tonapi.blockchain.execute_get_method(
            jetton_minter_address.to_string(),
            "get_wallet_address",
            owner_wallet_address_cell.to_boc(False).hex(),
        )
        if not response.stack or len(response.stack) == 0 or not response.stack[0].cell:
            return None

        wallet_address = parse_address_from_bytes(bytes.fromhex(response.stack[0].cell))
        if not wallet_address:
            return None

        await self._save_wallet_to_cache(
            owner_address=owner_address,
            jetton_minter_address=jetton_minter_address,
            jetton_wallet_address=wallet_address,
        )

        return wallet_address

    # === === === === ===

    async def get_account_transactions(
        self,
        account_address: TonAddress,
        limit: int = 10,
        before_lt: int | None = None,
        after_lt: int | None = None,
    ) -> List[TonTransaction]:

        transactions = await self.tonapi.blockchain.get_account_transactions(
            account_id=account_address.to_string(),
            limit=limit,
            before_lt=before_lt,
            after_lt=after_lt,
        )

        return [
            TransactionMapper().to_model(transaction=transaction)
            for transaction in transactions.transactions
        ]

    # === === === === ===

    async def get_all_jettons(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TonJettonInfo]:

        raw_jettons = await self.tonapi.jettons.get_all_jettons(limit=limit, offset=offset)

        return list(map(JettonInfoMapper.to_model, raw_jettons.jettons))

    # async def get_wallet_seqno(
    #     self,
    #     wallet_address: TonAddress,
    # ) -> int | None:

    #     return await self.tonapi.wallet.get_account_seqno(account_id=wallet_address.to_string())

    # # === === === === ===
    # async def get_account_info(
    #     self,
    #     account_address: TonAddress,
    # ) -> TonAccountInfo:

    #     account_info = await self.tonapi.accounts.get_info(account_id=account_address.to_string())
    #     return TonAccountInfo(
    #         address=TonAddress(account_info.address.to_userfriendly()),
    #         ton_balance=account_info.balance.to_nano(),
    #         status=account_info.status,
    #     )

    # # === === === === ===
    # async def get_jetton_balance(
    #     self,
    #     account_address: TonAddress,
    #     jetton_contract_address: TonAddress,
    # ) -> int:

    #     jettons_balances = await self.tonapi.accounts.get_jettons_balances(
    #         account_id=account_address.to_string()
    #     )

    #     for jetton_balance in jettons_balances.balances:
    #         if (
    #             TonAddress(jetton_balance.jetton.address.to_userfriendly())
    #             == jetton_contract_address
    #         ):
    #             return int(jetton_balance.balance)

    #     return 0

    # # === === === === ===
    # async def get_ico_buy_jetton_amount(
    #     self,
    #     ico_address: TonAddress,
    #     ton_amount: int,
    # ) -> int:

    #     response = await self.tonapi.blockchain.execute_get_method(
    #         ico_address.to_string(),
    #         "get_jetton_amount",
    #         str(ton_amount),
    #     )

    #     if not response.stack or len(response.stack) < 1 or not response.stack[0].num:
    #         raise Exception("Failed to get jetton wallet data")

    #     jetton_amount = int(response.stack[0].num, 16)

    #     return jetton_amount

    # # === === === === ===
    # async def get_ico_data(
    #     self,
    #     ico_contract_address: TonAddress,
    # ) -> IcoData:

    #     response = await self.tonapi.blockchain.execute_get_method(
    #         ico_contract_address.to_string(),
    #         "get_ico_data",
    #     )

    #     if not response.stack or len(response.stack) < 5:
    #         raise Exception("Failed to get Ico data")

    #     try:
    #         ico_data = IcoData(
    #             state=int(response.stack[0].num, 16),  # type: ignore
    #             price=int(response.stack[1].num, 16),  # type: ignore
    #             cap=int(response.stack[2].num, 16),  # type: ignore
    #             start_date=int(response.stack[3].num, 16),  # type: ignore
    #             end_date=int(response.stack[4].num, 16),  # type: ignore
    #         )
    #         return ico_data
    #     except Exception as e:
    #         raise Exception(f"Failed to get Ico data: {e}")

    # # === === === === ===
    # async def get_jetton_info(
    #     self,
    #     jetton_contract_address: TonAddress,
    # ) -> JettonShortInfo:

    #     jetton_info = await self.tonapi.jettons.get_info(
    #         account_id=jetton_contract_address.to_string()
    #     )

    #     return JettonShortInfo(
    #         symbol=jetton_info.metadata.symbol,
    #         decimals=int(jetton_info.metadata.decimals),
    #         total_supply=int(jetton_info.total_supply),
    #         contract_address=jetton_contract_address,
    #         image_url=jetton_info.metadata.image or "",
    #     )

    # # === === === === ===
    # async def get_liquidity_pool_data(
    #     self,
    #     pool_address: TonAddress,
    # ) -> LiquidityPoolData:

    #     response = await self.tonapi.blockchain.execute_get_method(
    #         pool_address.to_string(),
    #         "get_pool_data",
    #     )

    #     if not response.stack or len(response.stack) < 10:
    #         raise Exception("Failed to get liquidity pool data")

    #     try:
    #         reserve0 = int(response.stack[0].num, 16)  # type: ignore
    #         reserve1 = int(response.stack[1].num, 16)  # type: ignore
    #         token0_wallet_address = parse_address_from_bytes(bytes.fromhex(response.stack[2].cell))  # type: ignore  # noqa
    #         token1_wallet_address = parse_address_from_bytes(bytes.fromhex(response.stack[3].cell))  # type: ignore  # noqa
    #         lp_fee = int(response.stack[4].num, 16)  # type: ignore
    #         protocol_fee = int(response.stack[5].num, 16)  # type: ignore
    #         ref_fee = int(response.stack[6].num, 16)  # type: ignore
    #         protocol_fee_address = parse_address_from_bytes(bytes.fromhex(response.stack[7].cell))  # type: ignore  # noqa
    #         collected_token0_protocol_fee = int(response.stack[8].num, 16)  # type: ignore
    #         collected_token1_protocol_fee = int(response.stack[9].num, 16)  # type: ignore
    #     except Exception as e:
    #         raise Exception("Failed to get liquidity pool data. Error: %s", e)

    #     if not token0_wallet_address or not token1_wallet_address or not protocol_fee_address:
    #         raise Exception(
    #             "Failed to get liquidity pool data. Can't parse address from response stack: %s",
    #             response.stack,
    #         )

    #     pool_data = LiquidityPoolData(
    #         reserve0=reserve0,
    #         reserve1=reserve1,
    #         token0_wallet_address=TonAddress(token0_wallet_address),
    #         token1_wallet_address=TonAddress(token1_wallet_address),
    #         lp_fee=lp_fee,
    #         protocol_fee=protocol_fee,
    #         ref_fee=ref_fee,
    #         protocol_fee_address=TonAddress(protocol_fee_address),
    #         collected_token0_protocol_fee=collected_token0_protocol_fee,
    #         collected_token1_protocol_fee=collected_token1_protocol_fee,
    #     )

    #     return pool_data

    # === === === === === === ===

    async def get_public_key(
        self,
        wallet_address: TonAddress,
    ) -> str | None:

        response = await self.tonapi.accounts.get_public_key(wallet_address.to_string())
        return response.public_key

    # === === === === === === ===

    async def get_public_key_from_state_init(
        self,
        state_init: str,
    ) -> str | None:

        response = await self.tonapi.tonconnect.get_info_by_state_init(state_init=state_init)
        return response.public_key

    # === === === === === === ===

    async def get_balances(
        self,
        account_address: TonAddress,
    ) -> Balances:

        response = await self.tonapi.accounts.get_jettons_balances(account_address.to_string())
        jettons_balances = {
            TonAddress(item.jetton.address.to_userfriendly()): int(item.balance)
            for item in response.balances
        }

        response = await self.tonapi.accounts.get_info(account_address.to_string())
        ton_balance = int(response.balance.to_nano())

        balances = Balances(
            jettons=jettons_balances,
            ton=ton_balance,
        )

        return balances

    # === === === === === === ===

    async def get_jetton_info(
        self,
        minter_address: TonAddress,
    ) -> TonJettonInfo | None:

        try:
            response = await self.tonapi.jettons.get_info(minter_address.to_string())
            jetton_info = JettonInfoMapper.to_model(response)
        except Exception:
            return None

        return jetton_info

    # === === === === === === ===
