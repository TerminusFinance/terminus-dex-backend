# === === === === === === ===

import time
from datetime import timedelta

from pytoniq_core import Cell, begin_cell
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.constants import TonConstants
from src.config.config import Config
from src.features.ton_common.schemas.ton_prepared_transaction import (
    TonPreparedMessage,
    TonPreparedTransaction,
)
from src.utils.str_tools import bytes_to_b64str
from src.utils.ton_address import TonAddress


class LpWalletContract:

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

    async def prepare_burn_liquidity_transaction(
        self,
        lp_units: int,
        gas_amount: int | None = None,
        query_id: int = 0,
    ) -> TonPreparedTransaction:

        if not gas_amount:
            gas_amount = TonConstants.Fees.BURN_LIQUIDITY

        payload_cell = self.build_burn_body(
            amount=lp_units,
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

    def build_burn_body(
        self,
        amount: int,
        query_id: int = 0,
    ) -> Cell:

        cell = (
            begin_cell()
            .store_uint(TonConstants.OpCodes.BURN_LIQUIDITY, 32)
            .store_uint(query_id, 64)
            .store_coins(amount)
            .store_address(self.address.address)
            .end_cell()
        )

        return cell

    # === === === === === === ===
