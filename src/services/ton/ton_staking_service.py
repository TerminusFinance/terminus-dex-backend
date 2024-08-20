from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.config.config import Config
from src.database.repositories.ton import TonStakingContractRepository
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.features.ton_staking.schemas import (
    TonContractStakeData,
    TonStakingContractData,
    TonStakingPreparedTransactionData,
)
from src.features.ton_staking.staking_manager import TonStakingManager
from src.utils.ton_address import TonAddress


class TonStakingService:

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

    async def get_staking_contracts_data(self) -> List[TonStakingContractData]:
        """Retrieves staking contracts data.

        This function fetches data for all staking contracts from the database.
        It returns a list of `TonStakingContractData` objects, each containing
        the address, in_asset_address, and out_asset_address of a staking contract.

        Returns:
            List[TonStakingContractData]: A list of `TonStakingContractData` objects
                containing the data for all staking contracts.
        """

        staking_contract_repo = TonStakingContractRepository(self.session)
        staking_contracts_db = await staking_contract_repo.get_all()

        staking_contracts_data = [
            TonStakingContractData(
                address=TonAddress(contract.address),
                in_asset=TonAsset.from_db_model(contract.in_asset),
                out_asset=TonAsset.from_db_model(contract.out_asset),
                apy=contract.apy,
                fees=contract.fees,
                min_offer_amount=contract.min_offer_amount,
                is_active=contract.is_active,
            )
            for contract in staking_contracts_db
        ]

        return staking_contracts_data

    # === === === === === === ===

    async def get_contract_stake_data(
        self,
        contract_address: TonAddress,
    ) -> TonContractStakeData:
        """Retrieves stake data from the staking contract.

        This function fetches stake data from the staking contract specified by
        the `contract_address`. It returns a `TonContractStakeData` object
        containing the stake data.

        Args:
            contract_address (TonAddress): The address of the staking contract
                to fetch stake data from.

        Returns:
            TonContractStakeData: A `TonContractStakeData` object containing the
                stake data from the staking contract.

        Raises:
            StakingContractNotFoundError: If the staking contract is not found
                in the database.
            GetMethodExecutionError: If the execution of the `get_stake_data`
                method fails.
            GetStakeDataError: If the method execution succeeds but the returned
                stack size is not 2 or if the stack data is not valid.
        """

        staking_manager = TonStakingManager(
            session=self.session, config=self.config, ton_client=self.ton_client
        )
        contract = await staking_manager.get_contract(address=contract_address)
        stake_data = await contract.get_stake_data()

        return stake_data

    # === === === === === === ===

    async def get_prepared_stake_transaction(
        self,
        offer_amount: int,
        contract_address: TonAddress,
    ) -> TonStakingPreparedTransactionData:
        """Prepares a transaction for staking.

        This function creates a transfer message to the staking contract with the
        specified `offer_amount` and returns a `TonPreparedTransaction` containing
        the prepared transfer message.

        Args:
            offer_amount (int): The amount of tokens to stake.
            contract_address (TonAddress): The address of the staking contract to
                stake to.

        Returns:
            TonStakingPreparedTransactionData: Object containing the prepared transaction and
                expected amount.

        Raises:
            StakingContractNotFoundError: If the staking contract is not found
                in the database.
        """

        staking_manager = TonStakingManager(
            session=self.session, config=self.config, ton_client=self.ton_client
        )
        contract = await staking_manager.get_contract(address=contract_address)

        expected_amount = await contract.get_jetton_amount(offer_amount=offer_amount)
        prepared_stake_transaction = await contract.get_prepared_stake_transaction(
            offer_amount=offer_amount
        )

        transaction_data = TonStakingPreparedTransactionData(
            transaction=prepared_stake_transaction,
            expected_amount=expected_amount,
        )

        return transaction_data

    # === === === === === === ===
