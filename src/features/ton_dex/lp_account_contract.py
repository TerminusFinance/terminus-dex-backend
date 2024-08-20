import time
from datetime import timedelta

from pytoniq_core import Cell, begin_cell
from src.blockchains.ton.clients.exceptions import (
    TonGetMethodNotFoundError,
    TonGetMethodResultValidationError,
)
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.clients.utils import parse_address_from_cell_str
from src.blockchains.ton.constants import TonConstants
from src.config.config import Config
from src.features.ton_common.schemas.ton_prepared_transaction import (
    TonPreparedMessage,
    TonPreparedTransaction,
)
from src.utils.str_tools import bytes_to_b64str
from src.utils.ton_address import TonAddress

from .schemas import LpAccountData

# === === === === === === ===


class LpAccountContract:

    # === === === === === === ===

    def __init__(
        self,
        address: TonAddress,
        ton_client: TonClient,
        config: Config,
    ) -> None:

        self.address = address
        self.ton_client = ton_client
        self.config = config

    # === === === === === === ===

    async def prepare_activate_liquidity_transaction(
        self,
        first_token_units: int,
        second_token_units: int,
        min_lp_out_units: int,
        gas_amount: int | None = None,
    ) -> TonPreparedTransaction:

        if not gas_amount:
            gas_amount = TonConstants.Fees.DIRECT_ADD_LP

        payload_cell = self.build_activate_liquidity_body(
            token_0_amount=first_token_units,
            token_1_amount=second_token_units,
            min_lp_out_units=min_lp_out_units,
        )
        payload = bytes_to_b64str(payload_cell.to_boc())

        message = TonPreparedMessage(
            address=self.address.to_string(),
            amount=gas_amount,
            payload=payload,
        )

        valid_until = int(
            time.time()
            + timedelta(
                minutes=TonConstants.TonConnect.PREPARED_TRANSACTION_LIFETIME_MINUTES
            ).total_seconds()
        )

        transaction_data = TonPreparedTransaction(
            valid_until=valid_until,
            network=self.config.get_workchain_id(),
            messages=[message],
        )

        return transaction_data

    # === === === === === === ===

    async def prepare_refund_transaction(
        self,
        gas_amount: int | None = None,
        query_id: int = 0,
    ) -> TonPreparedTransaction:

        if not gas_amount:
            gas_amount = TonConstants.Fees.REFUND

        payload_cell = self.build_refund_body(
            query_id=query_id,
        )
        payload = bytes_to_b64str(payload_cell.to_boc())

        message = TonPreparedMessage(
            address=self.address.to_string(),
            amount=gas_amount,
            payload=payload,
        )

        valid_until = int(
            time.time()
            + timedelta(
                minutes=TonConstants.TonConnect.PREPARED_TRANSACTION_LIFETIME_MINUTES
            ).total_seconds()
        )

        transaction_data = TonPreparedTransaction(
            valid_until=valid_until,
            network=self.config.get_workchain_id(),
            messages=[message],
        )

        return transaction_data

    # === === === === === === ===

    async def get_lp_account_data(
        self,
    ) -> LpAccountData | None:

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_lp_account_data",
            )
        except TonGetMethodNotFoundError:
            return None

        if (
            not response.success
            or not response.stack
            or len(response.stack) != 4
            or not response.stack[0].cell
            or not response.stack[1].cell
            or not response.stack[2].num
            or not response.stack[3].num
        ):
            raise TonGetMethodResultValidationError()

        owner_address = parse_address_from_cell_str(response.stack[0].cell)
        pool_address = parse_address_from_cell_str(response.stack[1].cell)

        if not owner_address or not pool_address:
            raise TonGetMethodResultValidationError()

        token_0_balance = int(response.stack[2].num, 16)
        token_1_balance = int(response.stack[3].num, 16)

        return LpAccountData(
            owner_address=owner_address,
            pool_address=pool_address,
            token_0_balance=token_0_balance,
            token_1_balance=token_1_balance,
        )

    # === === === === === === ===

    def build_activate_liquidity_body(
        self,
        token_0_amount: int,
        token_1_amount: int,
        min_lp_out_units: int,
        query_id: int = 0,
    ) -> Cell:

        cell = (
            begin_cell()
            .store_uint(TonConstants.OpCodes.DIRECT_ADD_LIQUIDITY, 32)
            .store_uint(query_id, 64)
            .store_coins(token_0_amount)
            .store_coins(token_1_amount)
            .store_coins(min_lp_out_units)
            .end_cell()
        )

        return cell

    # === === === === === === ===

    def build_refund_body(
        self,
        query_id: int = 0,
    ) -> Cell:

        cell = (
            begin_cell()
            .store_uint(TonConstants.OpCodes.REFUND_ME, 32)
            .store_uint(query_id, 64)
            .end_cell()
        )

        return cell

    # === === === === === === ===
