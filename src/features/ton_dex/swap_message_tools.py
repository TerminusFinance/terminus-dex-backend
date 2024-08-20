from pytoniq_core import Cell, begin_cell
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.constants import TonConstants
from src.blockchains.ton.utils.jetton import create_jetton_transfer_body
from src.features.ton_common.schemas.ton_prepared_transaction import TonPreparedTransaction
from src.utils.str_tools import bytes_to_b64str
from src.utils.ton_address import TonAddress


class SwapMessageTools:

    # === === === === === === ===
    def __init__(
        self,
        ton_client: TonClient,
        router_address: TonAddress,
    ) -> None:

        self.ton_client = ton_client
        self.router_address = router_address

    # === === === === === === ===
    def create_swap_body(
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

    # === === === === === === ===
    async def build_swap_jetton_tx_params(
        self,
        user_wallet_address: TonAddress,
        offer_jetton_contract_address: TonAddress,
        ask_jetton_contract_address: TonAddress,
        offer_amount: int,
        min_ask_amount: int,
        gas_amount: int | None = None,
        forward_gas_amount: int | None = None,
        referral_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedTransaction:

        if gas_amount is None:
            gas_amount = TonConstants.Fees.SWAP
        if forward_gas_amount is None:
            forward_gas_amount = TonConstants.Fees.SWAP_FORWARD
        if query_id is None:
            query_id = 0

        offer_jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=offer_jetton_contract_address,
            owner_address=user_wallet_address,
        )
        ask_jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=ask_jetton_contract_address,
            owner_address=self.router_address,
        )

        forward_payload_cell = self.create_swap_body(
            user_wallet_address=user_wallet_address,
            min_ask_amount=min_ask_amount,
            ask_jetton_wallet_address=ask_jetton_wallet_address,
            referral_address=referral_address,
        )
        payload_cell = create_jetton_transfer_body(
            to_address=self.router_address,
            jetton_amount=offer_amount,
            forward_payload=forward_payload_cell,
            forward_amount=forward_gas_amount,
            response_address=user_wallet_address,
            query_id=query_id,
        )
        payload = bytes_to_b64str(payload_cell.to_boc())

        message = TonPreparedTransaction(
            address=offer_jetton_wallet_address.to_string(),
            payload=payload,
            amount=gas_amount,
        )
        return message

    # === === === === === === ===
    async def build_swap_proxy_ton_tx_params(
        self,
        user_wallet_address: TonAddress,
        proxy_ton_address: TonAddress,
        ask_jetton_contract_address: TonAddress,
        offer_amount: int,
        min_ask_amount: int,
        forward_gas_amount: int | None = None,
        referral_address: TonAddress | None = None,
        query_id: int | None = None,
    ) -> TonPreparedTransaction:

        if forward_gas_amount is None:
            forward_gas_amount = TonConstants.Fees.SWAP_FORWARD
        if query_id is None:
            query_id = 0
        gas_amount = forward_gas_amount + offer_amount

        proxy_ton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=proxy_ton_address,
            owner_address=self.router_address,
        )
        ask_jetton_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=ask_jetton_contract_address,
            owner_address=self.router_address,
        )

        forward_payload_cell = self.create_swap_body(
            user_wallet_address=user_wallet_address,
            min_ask_amount=min_ask_amount,
            ask_jetton_wallet_address=ask_jetton_wallet_address,
            referral_address=referral_address,
        )
        payload_cell = create_jetton_transfer_body(
            to_address=self.router_address,
            jetton_amount=offer_amount,
            forward_payload=forward_payload_cell,
            forward_amount=forward_gas_amount,
            response_address=user_wallet_address,
            query_id=query_id,
        )
        payload = bytes_to_b64str(payload_cell.to_boc())

        message = TonPreparedTransaction(
            address=proxy_ton_wallet_address.to_string(),
            payload=payload,
            amount=gas_amount,
        )

        return message
