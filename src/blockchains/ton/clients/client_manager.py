from typing import Literal

from src.blockchains.ton.clients.ton_client import TonClient
from src.config import Config
from src.utils.singleton import SingletonMeta

from .tonapi_client.tonapi_client import TonApiClient

# === === === === === === ===


class TonClientManager(metaclass=SingletonMeta):

    # === === === === === === ===

    def __init__(
        self,
        config: Config,
    ) -> None:

        self.config = config
        self.tonapi_client: TonClient | None = None

    # === === === === === === ===

    def get_ton_client(
        self,
        client_type: Literal["tonapi"] = "tonapi",
    ) -> TonClient:

        if client_type == "tonapi":
            if self.tonapi_client is None:
                self.tonapi_client = TonApiClient(config=self.config)
            return self.tonapi_client

        raise Exception(f"Unknown client type: {client_type}. Available types: 'tonapi'")

    # === === === === === === ===
