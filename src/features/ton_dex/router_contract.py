# === === === === === === ===

import time
from collections import defaultdict
from datetime import timedelta
from typing import Dict

from pytoniq_core import Cell, begin_cell
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.clients.utils import parse_address_from_cell_str
from src.blockchains.ton.constants import TonConstants
from src.blockchains.ton.utils.jetton import (
    create_jetton_transfer_body,
    create_jetton_transfer_payload,
)
from src.config.config import Config
from src.features.ton_common.schemas.ton_prepared_transaction import (
    TonPreparedMessage,
    TonPreparedTransaction,
)
from src.utils.str_tools import bytes_to_b64str
from src.utils.ton_address import TonAddress

# === === === === === === ===


class TonDexRouterContract:

    pool_addresses_cache: Dict[TonAddress, Dict[TonAddress, TonAddress]] = defaultdict(lambda: {})

    # === === === === === === ===

    def __init__(
        self,
        ton_client: TonClient,
        config: Config,
        address: TonAddress,
        proxy_ton_address: TonAddress,
    ) -> None:

        self.ton_client = ton_client
        self.config = config
        self.address = address
        self.proxy_ton_address = proxy_ton_address

    # === === === Swap === === ===
    # ============================

    async def prepare_swap_transaction(
        self,
        account_address: TonAddress,
        ask_jetton_address: TonAddress,
        offer_jetton_address: TonAddress,
        offer_units: int,
        min_ask_units: int,
        referral_address: TonAddress | None = None,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedTransaction:

        swap_message = await self.prepare_swap_message(
            user_wallet_address=account_address,
            ask_jetton_address=ask_jetton_address,
            offer_jetton_address=offer_jetton_address,
            offer_units=offer_units,
            min_ask_units=min_ask_units,
            referral_address=referral_address,
            forward_gas_amount=forward_gas_amount,
            response_address=response_address or account_address,
            query_id=query_id,
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
            messages=[swap_message],
        )

    # === === === === === === ===

    async def prepare_swap_message(
        self,
        user_wallet_address: TonAddress,
        ask_jetton_address: TonAddress,
        offer_jetton_address: TonAddress,
        offer_units: int,
        min_ask_units: int,
        referral_address: TonAddress | None = None,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedMessage:

        if offer_jetton_address == TonConstants.ContractAddresses.TON:
            swap_message = await self.prepare_swap_ton_message(
                user_wallet_address=user_wallet_address,
                proxy_ton_address=self.proxy_ton_address,
                ask_jetton_contract_address=ask_jetton_address,
                offer_amount=offer_units,
                min_ask_amount=min_ask_units,
                referral_address=referral_address,
                forward_gas_amount=forward_gas_amount,
                response_address=response_address or user_wallet_address,
                query_id=query_id,
            )
        else:
            if ask_jetton_address == TonConstants.ContractAddresses.TON:
                ask_jetton_address = self.proxy_ton_address

            swap_message = await self.prepare_swap_jetton_message(
                user_wallet_address=user_wallet_address,
                offer_jetton_contract_address=offer_jetton_address,
                ask_jetton_contract_address=ask_jetton_address,
                offer_amount=offer_units,
                min_ask_amount=min_ask_units,
                referral_address=referral_address,
                forward_gas_amount=forward_gas_amount,
                response_address=response_address or user_wallet_address,
                query_id=query_id,
            )

        return swap_message

    # === === === === === === ===

    async def prepare_swap_jetton_message(
        self,
        user_wallet_address: TonAddress,
        offer_jetton_contract_address: TonAddress,
        ask_jetton_contract_address: TonAddress,
        offer_amount: int,
        min_ask_amount: int,
        gas_amount: int | None = None,
        referral_address: TonAddress | None = None,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedMessage:

        if gas_amount is None:
            gas_amount = (
                TonConstants.Fees.SWAP
                if ask_jetton_contract_address != self.proxy_ton_address
                else TonConstants.Fees.SWAP_JETTON_TO_TON
            )
        if forward_gas_amount is None:
            forward_gas_amount = (
                TonConstants.Fees.SWAP_FORWARD
                if ask_jetton_contract_address != self.proxy_ton_address
                else TonConstants.Fees.SWAP_JETTON_TO_TON_FORWARD
            )
        if query_id is None:
            query_id = 0

        offer_jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=offer_jetton_contract_address,
            owner_address=user_wallet_address,
        )
        ask_jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=ask_jetton_contract_address,
            owner_address=self.address,
        )

        forward_payload_cell = self.build_swap_body(
            user_wallet_address=user_wallet_address,
            min_ask_amount=min_ask_amount,
            ask_jetton_wallet_address=ask_jetton_wallet_address,
            referral_address=referral_address,
        )
        payload_cell = create_jetton_transfer_body(
            to_address=self.address,
            jetton_amount=offer_amount,
            forward_payload=forward_payload_cell,
            forward_amount=forward_gas_amount,
            response_address=response_address or user_wallet_address,
            query_id=query_id,
        )
        payload = bytes_to_b64str(payload_cell.to_boc())

        message = TonPreparedMessage(
            address=offer_jetton_wallet_address.to_string(),
            payload=payload,
            amount=gas_amount,
        )
        return message

    # === === === === === === ===

    async def prepare_swap_ton_message(
        self,
        user_wallet_address: TonAddress,
        proxy_ton_address: TonAddress,
        ask_jetton_contract_address: TonAddress,
        offer_amount: int,
        min_ask_amount: int,
        referral_address: TonAddress | None = None,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedMessage:

        if forward_gas_amount is None:
            forward_gas_amount = TonConstants.Fees.SWAP_TON_TO_JETTON_FORWARD
        if query_id is None:
            query_id = 0
        gas_amount = forward_gas_amount + offer_amount

        proxy_ton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=proxy_ton_address,
            owner_address=self.address,
        )
        ask_jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=ask_jetton_contract_address,
            owner_address=self.address,
        )

        forward_payload_cell = self.build_swap_body(
            user_wallet_address=user_wallet_address,
            min_ask_amount=min_ask_amount,
            ask_jetton_wallet_address=ask_jetton_wallet_address,
            referral_address=referral_address,
        )
        payload_cell = create_jetton_transfer_body(
            to_address=self.address,
            jetton_amount=offer_amount,
            forward_payload=forward_payload_cell,
            forward_amount=forward_gas_amount,
            response_address=response_address or user_wallet_address,
            query_id=query_id,
        )
        payload = bytes_to_b64str(payload_cell.to_boc())

        message = TonPreparedMessage(
            address=proxy_ton_wallet_address.to_string(),
            payload=payload,
            amount=gas_amount,
        )

        return message

    # === === === === === === ===

    def build_swap_body(
        self,
        user_wallet_address: TonAddress,
        min_ask_amount: int,
        ask_jetton_wallet_address: TonAddress,
        referral_address: TonAddress | None = None,
    ) -> Cell:

        cell_builder = (
            begin_cell()
            .store_uint(TonConstants.OpCodes.SWAP, 32)
            .store_address(ask_jetton_wallet_address.address)
            .store_coins(min_ask_amount)
            .store_address(user_wallet_address.address)
        )
        if referral_address:
            cell_builder.store_uint(1, 1).store_address(referral_address.address)
        else:
            cell_builder.store_uint(0, 1)
        cell = cell_builder.end_cell()

        return cell

    # === === end Swap === === ===
    # ============================

    # === === === Liquidity === === ===
    # =================================

    async def prepare_provide_liquidity_transaction(
        self,
        account_address: TonAddress,
        token_address_0: TonAddress,
        token_address_1: TonAddress,
        amount_0: int,
        amount_1: int,
        min_lp_out_units: int,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id_0: int | None = None,
        query_id_1: int | None = None,
    ) -> TonPreparedTransaction:

        message_0 = await self.prepare_provide_liquidity_message(
            account_address=account_address,
            send_token_address=token_address_0,
            pair_token_address=token_address_1,
            units=amount_0,
            min_lp_out_units=min_lp_out_units,
            forward_gas_amount=forward_gas_amount,
            response_address=response_address or account_address,
            query_id=query_id_0,
        )
        message_1 = await self.prepare_provide_liquidity_message(
            account_address=account_address,
            send_token_address=token_address_1,
            pair_token_address=token_address_0,
            units=amount_1,
            min_lp_out_units=min_lp_out_units,
            forward_gas_amount=forward_gas_amount,
            response_address=response_address or account_address,
            query_id=query_id_1,
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
            messages=[message_0, message_1],
        )

    # === === === === === === ===

    async def prepare_single_side_provide_liquidity_transaction(
        self,
        account_address: TonAddress,
        send_token_address: TonAddress,
        pair_token_address: TonAddress,
        send_units: int,
        min_lp_out_units: int,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedTransaction:

        provide_liquidity_message = await self.prepare_provide_liquidity_message(
            account_address=account_address,
            send_token_address=send_token_address,
            pair_token_address=pair_token_address,
            units=send_units,
            min_lp_out_units=min_lp_out_units,
            forward_gas_amount=forward_gas_amount,
            response_address=response_address or account_address,
            query_id=query_id,
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
            messages=[provide_liquidity_message],
        )

    # === === === === === === ===

    async def prepare_provide_liquidity_message(
        self,
        account_address: TonAddress,
        send_token_address: TonAddress,
        pair_token_address: TonAddress,
        units: int,
        min_lp_out_units: int,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedMessage:

        if send_token_address == TonConstants.ContractAddresses.TON:
            message = await self.prepare_provide_ton_liquidity_message(
                account_address=account_address,
                proxy_ton_address=self.proxy_ton_address,
                pair_token_address=pair_token_address,
                ton_units=units,
                min_lp_out_units=min_lp_out_units,
                forward_gas_amount=forward_gas_amount,
                response_address=response_address or account_address,
                query_id=query_id,
            )
        else:
            if pair_token_address == TonConstants.ContractAddresses.TON:
                pair_token_address = self.proxy_ton_address

            message = await self.prepare_provide_jetton_liquidity_message(
                account_address=account_address,
                send_token_address=send_token_address,
                pair_token_address=pair_token_address,
                units=units,
                min_lp_out_units=min_lp_out_units,
                forward_gas_amount=forward_gas_amount,
                response_address=response_address or account_address,
                query_id=query_id,
            )

        return message

    # === === === === === === ===

    async def prepare_provide_jetton_liquidity_message(
        self,
        account_address: TonAddress,
        send_token_address: TonAddress,
        pair_token_address: TonAddress,
        units: int,
        min_lp_out_units: int,
        gas_amount: int | None = None,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedMessage:

        if gas_amount is None:
            gas_amount = TonConstants.Fees.PROVIDE_LP
        if forward_gas_amount is None:
            forward_gas_amount = TonConstants.Fees.PROVIDE_LP_JETTON_FORWARD
        if query_id is None:
            query_id = 0

        jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=send_token_address,
            owner_address=account_address,
        )
        router_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=pair_token_address,
            owner_address=self.address,
        )

        forward_payload_cell = self.build_provide_liquidity_body(
            router_wallet_address=router_wallet_address,
            min_lp_out_units=min_lp_out_units,
        )
        payload = create_jetton_transfer_payload(
            to_address=self.address,
            jetton_amount=units,
            forward_amount=forward_gas_amount,
            forward_payload=forward_payload_cell,
            response_address=response_address,
            query_id=query_id,
        )

        message = TonPreparedMessage(
            address=jetton_wallet_address.to_string(),
            amount=gas_amount,
            payload=payload,
        )

        return message

    # === === === === === === ===

    async def prepare_provide_ton_liquidity_message(
        self,
        account_address: TonAddress,
        proxy_ton_address: TonAddress,
        pair_token_address: TonAddress,
        ton_units: int,
        min_lp_out_units: int,
        forward_gas_amount: int | None = None,
        response_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedMessage:

        gas_amount = TonConstants.Fees.PROVIDE_LP
        if forward_gas_amount is None:
            forward_gas_amount = TonConstants.Fees.PROVIDE_LP_TON_FORWARD
        if query_id is None:
            query_id = 0
        gas_amount = forward_gas_amount + ton_units

        proxy_ton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=proxy_ton_address,
            owner_address=self.address,
        )
        router_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=pair_token_address,
            owner_address=self.address,
        )

        forward_payload = self.build_provide_liquidity_body(
            router_wallet_address=router_wallet_address,
            min_lp_out_units=min_lp_out_units,
        )
        payload = create_jetton_transfer_payload(
            to_address=self.address,
            jetton_amount=ton_units,
            forward_amount=forward_gas_amount,
            forward_payload=forward_payload,
            response_address=response_address or account_address,
            query_id=query_id,
        )

        message_data = TonPreparedMessage(
            address=proxy_ton_wallet_address.to_string(),
            amount=gas_amount,
            payload=payload,
        )

        return message_data

    # === === === === === === ===

    def build_provide_liquidity_body(
        self,
        router_wallet_address: TonAddress,
        min_lp_out_units: int,
    ) -> Cell:

        cell = (
            begin_cell()
            .store_uint(TonConstants.OpCodes.PROVIDE_LIQUIDITY, 32)
            .store_address(router_wallet_address.address)
            .store_coins(min_lp_out_units)
            .end_cell()
        )

        return cell

    # === === end Liquidity === === ===
    # =================================

    # === === === Get Methods === === ===
    # ===================================

    async def get_pool_address(
        self,
        token_0_address: TonAddress,
        token_1_address: TonAddress,
    ) -> TonAddress | None:

        # TODO: Add cache

        if token_0_address == TonConstants.ContractAddresses.TON:
            token_0_address = self.proxy_ton_address

        if token_1_address == TonConstants.ContractAddresses.TON:
            token_1_address = self.proxy_ton_address

        pool_address = TonDexRouterContract.pool_addresses_cache[token_0_address].get(
            token_1_address
        )

        if pool_address:
            return pool_address

        token_0_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=token_0_address,
            owner_address=self.address,
        )
        token_1_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=token_1_address,
            owner_address=self.address,
        )

        response = await self.ton_client.run_get_method(
            self.address,
            "get_pool_address",
            token_0_wallet_address.to_string(),
            token_1_wallet_address.to_string(),
        )
        if not response.success or not response.stack:
            return None
        if not response.stack[0].cell:
            return None
        address = parse_address_from_cell_str(response.stack[0].cell)
        if not address:
            return None

        TonDexRouterContract.pool_addresses_cache[token_0_address][token_1_address] = address
        TonDexRouterContract.pool_addresses_cache[token_1_address][token_0_address] = address

        return TonAddress(address)

    # === === end Get Methods === === ===
    # ===================================
