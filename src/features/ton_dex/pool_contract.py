# === === === === === === ===

from typing import Dict

from src.blockchains.ton.clients.exceptions import (
    TonGetMethodNotFoundError,
    TonGetMethodResultValidationError,
)
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.clients.utils import parse_address_from_cell_str
from src.blockchains.ton.schemas._models import JettonData
from src.features.ton_common.jetton_minter_contract import JettonMinterContract
from src.utils.ton_address import TonAddress

from .schemas import ExpectedLiquidityData, PoolData

# === === === === === === ===


class PoolContract:

    lp_account_addresses_cache: Dict[TonAddress, TonAddress] = {}

    # === === === === === === ===

    def __init__(
        self,
        address: TonAddress,
        ton_client: TonClient,
    ) -> None:

        self.address = address
        self.ton_client = ton_client
        self.minter_contract = JettonMinterContract(address=address, ton_client=ton_client)

    # === === === Get Methods === === ===
    # ===================================

    async def get_pool_data(
        self,
    ) -> PoolData | None:

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_pool_data",
            )
        except TonGetMethodNotFoundError:
            return None

        if not response or not response.stack:
            raise TonGetMethodResultValidationError("No response or stack.")

        if (
            len(response.stack) < 10
            or not response.stack[0].num
            or not response.stack[1].num
            or not response.stack[2].cell
            or not response.stack[3].cell
            or not response.stack[4].num
            or not response.stack[5].num
            or not response.stack[6].num
            or not response.stack[7].cell
            or not response.stack[8].num
            or not response.stack[9].num
        ):
            raise TonGetMethodResultValidationError("Wrong stack data.")

        token0_wallet_address = parse_address_from_cell_str(response.stack[2].cell)
        token1_wallet_address = parse_address_from_cell_str(response.stack[3].cell)
        protocol_fee_address = parse_address_from_cell_str(response.stack[7].cell)

        if not token0_wallet_address or not token1_wallet_address or not protocol_fee_address:
            raise TonGetMethodResultValidationError("Wrong stack data.")

        reserve0 = int(response.stack[0].num, 16)
        reserve1 = int(response.stack[1].num, 16)
        lp_fee = int(response.stack[4].num, 16)
        protocol_fee = int(response.stack[5].num, 16)
        ref_fee = int(response.stack[6].num, 16)
        collected_token0_protocol_fee = int(response.stack[8].num, 16)
        collected_token1_protocol_fee = int(response.stack[9].num, 16)

        pool_data = PoolData(
            address=self.address,
            reserve_0=reserve0,
            reserve_1=reserve1,
            token_0_address=token0_wallet_address,
            token_1_address=token1_wallet_address,
            lp_fee=lp_fee,
            protocol_fee=protocol_fee,
            ref_fee=ref_fee,
            protocol_fee_address=protocol_fee_address,
            collected_token_0_protocol_fee=collected_token0_protocol_fee,
            collected_token_1_protocol_fee=collected_token1_protocol_fee,
        )

        return pool_data

    # === === === === === === ===

    async def get_jetton_data(
        self,
    ) -> JettonData | None:

        return await self.minter_contract.get_jetton_data()

    # === === === === === === ===

    async def get_expected_lp_tokens(
        self,
        token_0_amount: int,
        token_1_amount: int,
    ) -> int | None:

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_expected_tokens",
                f"{token_0_amount}",
                f"{token_1_amount}",
            )
        except TonGetMethodNotFoundError:
            return None

        if not response.success or not response.stack or not response.stack[0].num:
            raise TonGetMethodResultValidationError("Wrong stack data.")

        expected_tokens = int(response.stack[0].num, 16)

        return expected_tokens

    # === === === === === === ===

    async def get_lp_account_address(
        self,
        owner_address: TonAddress,
    ) -> TonAddress | None:

        lp_account_address = PoolContract.lp_account_addresses_cache.get(owner_address)

        if lp_account_address:
            return lp_account_address

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_lp_account_address",
                owner_address.to_string(),
            )
        except TonGetMethodNotFoundError:
            return None

        if not response.success or not response.stack or not response.stack[0].cell:
            raise TonGetMethodResultValidationError("Wrong stack data.")

        lp_account_address = parse_address_from_cell_str(response.stack[0].cell)

        if not lp_account_address:
            raise TonGetMethodResultValidationError("Wrong stack data.")

        PoolContract.lp_account_addresses_cache[owner_address] = lp_account_address

        return lp_account_address

    # === === === === === === ===

    async def get_expected_liquidity(
        self,
        lp_jetton_amount: int,
    ) -> ExpectedLiquidityData | None:

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_expected_liquidity",
                f"{lp_jetton_amount}",
            )
        except TonGetMethodNotFoundError:
            return None

        if (
            not response.success
            or len(response.stack) < 2
            or not response.stack[0].num
            or not response.stack[1].num
        ):
            raise TonGetMethodResultValidationError("Wrong stack data.")

        token_0_amount = int(response.stack[0].num, 16)
        token_1_amount = int(response.stack[1].num, 16)

        return ExpectedLiquidityData(
            token_0_amount=token_0_amount,
            token_1_amount=token_1_amount,
        )

    # === === end Get Methods === === ===
    # ===================================
