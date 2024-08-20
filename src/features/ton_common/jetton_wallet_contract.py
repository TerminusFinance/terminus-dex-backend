# === === === === === === ===

from src.blockchains.ton.clients.exceptions import (
    TonGetMethodNotFoundError,
    TonGetMethodResultValidationError,
)
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.clients.utils import parse_address_from_cell_str
from src.blockchains.ton.schemas._models import JettonWalletData
from src.utils.ton_address import TonAddress

# === === === === === === ===


class JettonWalletContract:

    # === === === === === === ===

    def __init__(
        self,
        address: TonAddress,
        ton_client: TonClient,
    ) -> None:

        self.address = address
        self.ton_client = ton_client

    # === === === === === === ===

    async def get_wallet_data(
        self,
    ) -> JettonWalletData | None:

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_wallet_data",
            )
        except TonGetMethodNotFoundError:
            return None

        if not response or not response.stack:
            raise TonGetMethodResultValidationError(
                "No response or stack."
                f" Address: {self.address.to_string()}."
                " Method: 'get_wallet_data'."
            )

        if (
            len(response.stack) < 4
            or not response.stack[0].num
            or not response.stack[1].cell
            or not response.stack[2].cell
            or not response.stack[3].cell
        ):
            raise TonGetMethodResultValidationError(
                "Wrong stack data."
                f" Address: {self.address.to_string()}."
                " Method: 'get_wallet_data'."
                f" Stack: {[item.type for item in response.stack]}"
            )

        balance = int(response.stack[0].num, 16)
        owner_wallet_address = parse_address_from_cell_str(response.stack[1].cell)
        minter_address = parse_address_from_cell_str(response.stack[2].cell)

        if not owner_wallet_address or not minter_address:
            raise TonGetMethodResultValidationError(
                "Can't parse owner or minter address."
                " Address: {self.address.to_string()}."
                " Method: 'get_wallet_data'."
            )

        return JettonWalletData(
            jetton_wallet_address=self.address,
            owner_wallet_address=owner_wallet_address,
            balance=balance,
            jetton_contract_address=minter_address,
        )

    # === === === === === === ===
