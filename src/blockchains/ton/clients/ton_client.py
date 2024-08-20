# === === === === === === ===

from abc import ABCMeta, abstractmethod
from typing import List

from src.blockchains.ton.schemas.ton_transaction import TonTransaction
from src.utils.ton_address import TonAddress

from ..schemas.balances import Balances
from ..schemas.get_method_result import GetMethodResult
from ..schemas.ton_jetton_info import TonJettonInfo

# === === === === === === ===


class TonClient(metaclass=ABCMeta):

    # === === === === === === ===

    async def run_get_method(
        self,
        address: TonAddress,
        method_name: str,
        *args: str | None,
    ) -> GetMethodResult:

        raise NotImplementedError()

    # === === === === ===
    # @abstractmethod
    # async def get_masterchain_block_shards(
    #     self,
    #     masterchain_block: TonBlock,
    # ) -> List[TonBlock]:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_block_transactions(
    #     self,
    #     block: TonBlock,
    # ) -> List[TonTransaction]:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_jetton_wallet_data(
    #     self,
    #     jetton_wallet_address: TonAddress,
    # ) -> JettonWalletData:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def send_message(
    #     self,
    #     message_boc: str,
    # ) -> bool:

    #     raise NotImplementedError()

    # # === === === === ===

    @abstractmethod
    async def get_jetton_wallet_address(
        self,
        jetton_minter_address: TonAddress,
        owner_address: TonAddress,
    ) -> TonAddress:

        raise NotImplementedError()

    # === === === === ===

    @abstractmethod
    async def get_account_transactions(
        self,
        account_address: TonAddress,
        limit: int = 10,
        before_lt: int | None = None,
        after_lt: int | None = None,
    ) -> List[TonTransaction]:

        raise NotImplementedError()

    # === === === === === === ===

    async def get_all_jettons(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TonJettonInfo]:

        raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_wallet_seqno(
    #     self,
    #     wallet_address: TonAddress,
    # ) -> int:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_account_info(
    #     self,
    #     account_address: TonAddress,
    # ) -> TonAccountInfo:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_jetton_balance(
    #     self,
    #     account_address: TonAddress,
    #     jetton_contract_address: TonAddress,
    # ) -> int:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_ico_buy_jetton_amount(
    #     self,
    #     ico_address: TonAddress,
    #     ton_amount: int,
    # ) -> int:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_ico_data(
    #     self,
    #     ico_contract_address: TonAddress,
    # ) -> IcoData:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_jetton_info(
    #     self,
    #     jetton_contract_address: TonAddress,
    # ) -> JettonShortInfo:

    #     raise NotImplementedError()

    # # === === === === ===
    # @abstractmethod
    # async def get_liquidity_pool_data(
    #     self,
    #     pool_address: TonAddress,
    # ) -> LiquidityPoolData:

    #     raise NotImplementedError()

    # === === === === === === ===

    @abstractmethod
    async def get_public_key(
        self,
        wallet_address: TonAddress,
    ) -> str | None:

        raise NotImplementedError()

    # === === === === === === ===

    @abstractmethod
    async def get_public_key_from_state_init(
        self,
        state_init: str,
    ) -> str | None:

        raise NotImplementedError()

    # === === === === === === ===

    @abstractmethod
    async def get_balances(
        self,
        account_address: TonAddress,
    ) -> Balances:

        raise NotImplementedError()

    # === === === === === === ===

    @abstractmethod
    async def get_jetton_info(
        self,
        minter_address: TonAddress,
    ) -> TonJettonInfo | None:

        raise NotImplementedError()

    # === === === === === === ===
