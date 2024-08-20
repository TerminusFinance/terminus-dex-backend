# === === === === === === ===

from src.blockchains.ton.clients.exceptions import (
    TonGetMethodNotFoundError,
    TonGetMethodResultValidationError,
)
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.clients.utils import parse_address_from_cell_str
from src.blockchains.ton.schemas._models import JettonData
from src.utils.ton_address import TonAddress

# === === === === === === ===


class JettonMinterContract:

    # === === === === === === ===

    def __init__(
        self,
        address: TonAddress,
        ton_client: TonClient,
    ) -> None:

        self.address = address
        self.ton_client = ton_client

    # === === === === === === ===

    async def get_jetton_data(
        self,
    ) -> JettonData | None:

        try:
            response = await self.ton_client.run_get_method(
                self.address,
                "get_jetton_data",
            )
        except TonGetMethodNotFoundError:
            return None

        if not response or not response.stack:
            raise TonGetMethodResultValidationError("No response or stack.")

        if (
            len(response.stack) < 5
            or not response.stack[0].num
            or not response.stack[1].num
            or not response.stack[2].cell
            or not response.stack[3].cell
            or not response.stack[4].cell
        ):
            raise TonGetMethodResultValidationError("Wrong stack data.")

        total_supply = int(response.stack[0].num, 16)
        mintable = bool(int(response.stack[1].num, 16))

        admin_address = parse_address_from_cell_str(response.stack[2].cell)
        if not admin_address:
            raise TonGetMethodResultValidationError("Wrong stack data.")

        return JettonData(
            total_supply=total_supply,
            mintable=mintable,
            admin_address=admin_address,
        )

    # === === === === === === ===
