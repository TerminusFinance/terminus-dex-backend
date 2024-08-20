from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.database.repositories.ton.ton_staking_contract_repo import TonStakingContractRepository
from src.exceptions.ton_staking_exceptions import StakingContractNotFoundError
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.utils.ton_address import TonAddress

from .jetton_staking_contract import JettonStakingContract


class TonStakingManager:

    # === === === === === === ===

    def __init__(
        self,
        session: AsyncSession,
        config: Config,
        ton_client: TonClient,
    ) -> None:

        self.session = session
        self.config = config
        self.ton_client = ton_client

    # === === === === === === ===

    async def get_contract(
        self,
        address: TonAddress,
    ) -> JettonStakingContract:
        """Get staking contract by address.

        Args:
            address (TonAddress): Address of the staking contract.

        Returns:
            TonStakingContract: Instance of the staking contract.

        Raises:
            StakingContractNotFoundError: If staking contract not found.
        """

        staking_contract_repo = TonStakingContractRepository(session=self.session)
        contract_db = await staking_contract_repo.get(address=address.to_string())

        if contract_db is None:
            raise StakingContractNotFoundError("Staking contract not found")

        in_asset = TonAsset.from_db_model(contract_db.in_asset)
        out_asset = TonAsset.from_db_model(contract_db.out_asset)
        contract = JettonStakingContract(
            address=TonAddress(contract_db.address),
            in_asset=in_asset,
            out_asset=out_asset,
            apy=contract_db.apy,
            ton_client=self.ton_client,
            config=self.config,
        )

        return contract

    # === === === === === === ===
