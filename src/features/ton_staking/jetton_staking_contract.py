from datetime import timedelta
from time import time

from pytoniq_core.boc import Cell, begin_cell
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.constants import TonConstants
from src.blockchains.ton.utils.jetton import create_jetton_transfer_payload
from src.config.config import Config
from src.exceptions.ton_client_exceptions import GetMethodExecutionError
from src.exceptions.ton_staking_exceptions import GetStakeDataError
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.features.ton_common.schemas.ton_prepared_transaction import TonPreparedTransaction
from src.features.ton_staking.schemas import TonContractStakeData
from src.utils.ton_address import TonAddress

# === === === === === === ===


def create_stake_forward_payload(query_id: int = 0) -> Cell:

    cell = (
        begin_cell()
        .store_uint(TonConstants.OpCodes.JETTON_STAKE, 32)
        .store_uint(query_id, 64)
        .end_cell()
    )

    return cell


# === === === === === === ===


class JettonStakingContract:
    stake_forward_amount: int = 50_000_000

    # === === === === === === ===
    def __init__(
        self,
        address: TonAddress,
        in_asset: TonAsset,
        out_asset: TonAsset,
        apy: float,
        ton_client: TonClient,
        config: Config,
    ) -> None:

        self.address = address
        self.in_asset = in_asset
        self.out_asset = out_asset
        self.apy = apy
        self.ton_client = ton_client
        self.config = config

    # === === === === === === ===

    async def get_stake_data(self) -> TonContractStakeData:
        """Retrieves stake data from the staking contract.

        This function sends a `get_stake_data` method to the staking contract and
        returns a `TonContractStakeData` containing the stake data.

        Returns:
            `TonContractStakeData`: a `TonContractStakeData` containing the stake data
                from the staking contract.

        Raises:
            `GetMethodExecutionError`: if the execution of the `get_stake_data` method
                fails.
            `GetStakeDataError`: if the method execution succeeds but the returned
                stack size is not 2 or if the stack data is not valid.
        """

        result = await self.ton_client.run_get_method(
            address=self.address,
            method_name="get_staking_data",
        )

        if not result.success:
            raise GetMethodExecutionError("Exit code: %d", result.exit_code)

        if len(result.stack) < 2:
            raise GetStakeDataError("Wrong stack size.")

        if not result.stack[0].num or not result.stack[1].num:
            raise GetStakeDataError("Wrong stack data")

        is_active = int(result.stack[0].num, 16) == 0  # active if 0
        price = int(result.stack[1].num, 16)

        return TonContractStakeData(address=self.address, price=price, is_active=is_active)

    # === === === === === === ===

    async def get_prepared_stake_transaction(
        self,
        offer_amount: int,
    ) -> TonPreparedTransaction:
        """Prepares a transaction for staking.

        This function creates a transfer message to the staking contract with the
        specified `offer_amount` and returns a `TonPreparedTransaction` containing
        the prepared transfer message.

        Args:
            offer_amount (int): The amount of tokens to stake.

        Returns:
            `TonPreparedTransaction`: A `TonPreparedTransaction` containing the
                prepared transfer message for staking.
        """

        payload = create_jetton_transfer_payload(
            to_address=self.address,
            jetton_amount=offer_amount,
            forward_amount=100,
            forward_payload=create_stake_forward_payload(),
        )

        message = TonPreparedTransaction(
            address=self.address.to_string(),
            amount=self.stake_forward_amount,
            payload=payload,
        )

        valid_until = int(
            time.time()
            + timedelta(
                minutes=TonConstants.TonConnect.PREPARED_TRANSACTION_LIFETIME_MINUTES
            ).total_seconds()
        )

        return TonPreparedTransaction(
            valid_until=valid_until,
            network=self.config.get_workchain_id(),
            messages=[message],
        )

    # === === === === === === ===

    async def get_jetton_amount(
        self,
        offer_amount: int,
    ) -> int:

        response = await self.ton_client.run_get_method(
            self.address,
            "get_jetton_amount",
            f"{offer_amount}",
        )

        if not response.success:
            return None
        if not response.stack or not response.stack[0].num:
            return None

        jetton_amount = int(response.stack[0].num, 16)

        return jetton_amount

    # === === === === === === ===
