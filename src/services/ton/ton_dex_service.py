# === === === === === === ===

from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.constants import TonConstants
from src.config.config import Config
from src.database.repositories.ton.ton_asset_repository import TonAssetRepository
from src.database.repositories.ton.ton_dex_pool_repository import TonDexPoolRepository
from src.exceptions.ton_dex_exceptions import (
    LpAccountAddressNotFoundError,
    LpWalletAddressNotFoundError,
    PoolAddressNotFoundError,
)
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.features.ton_common.schemas.ton_prepared_transaction import (
    TonPreparedMessage,
    TonPreparedTransaction,
)
from src.features.ton_dex.lp_account_contract import LpAccountContract
from src.features.ton_dex.lp_wallet_contract import LpWalletContract
from src.features.ton_dex.params_manager import DexParamsManager, SwapType
from src.features.ton_dex.pool_contract import PoolContract
from src.features.ton_dex.router_contract import TonDexRouterContract
from src.features.ton_dex.schemas import TonBaseProvideLiquidityParams, TonSwapParams
from src.utils.ton_address import TonAddress

# === === === === === === ===


class TonDexService:

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

    async def get_assets(
        self,
        limit: int = 100,
        offset: int = 0,
        all: bool = True,
        exclude_community: bool = False,
        exclude_blacklisted: bool = False,
        exclude_deprecated: bool = False,
        exclude_deleted: bool = True,
    ) -> List[TonAsset]:

        assets_repo = TonAssetRepository(session=self.session)
        assets_db = await assets_repo.get_all(
            limit=limit,
            offset=offset,
            all=all,
            exclude_community=exclude_community,
            exclude_blacklisted=exclude_blacklisted,
            exclude_deprecated=exclude_deprecated,
            exclude_deleted=exclude_deleted,
        )

        assets = [TonAsset.from_db_model(asset) for asset in assets_db]

        return assets

    # === === === === === === ===

    async def get_assets_pairs(
        self,
    ) -> List[Tuple[str, str]]:

        pool_repo = TonDexPoolRepository(session=self.session)
        pools_db = await pool_repo.get_all()

        return [
            (
                self.swap_proxy_to_ton_address(
                    TonAddress(pool.token_0_minter_address)
                ).to_string(),
                self.swap_proxy_to_ton_address(
                    TonAddress(pool.token_1_minter_address)
                ).to_string(),
            )
            for pool in pools_db
        ]

    # === === === === === === ===

    async def find_asset(
        self,
        address: TonAddress,
        account_address: TonAddress | None = None,
    ) -> TonAsset | None:

        asset_repo = TonAssetRepository(session=self.session)
        asset_db = await asset_repo.get(address=address)

        if asset_db:
            return TonAsset.from_db_model(asset_db)

        jetton_info = await self.ton_client.get_jetton_info(minter_address=address)

        if jetton_info is None:
            return None

        asset = TonAsset.from_jetton_info(jetton_info)

        await asset_repo.create(
            address=asset.address,
            symbol=asset.symbol,
            name=asset.name,
            image_url=asset.image_url,
            decimals=asset.decimals,
            is_community=asset.is_community,
            is_deprecated=asset.is_deprecated,
            is_blacklisted=asset.is_blacklisted,
            account_address=account_address if account_address else None,
        )

        return asset

    # === === === === === === ===

    async def get_swap_params(
        self,
        offer_address: TonAddress,
        ask_address: TonAddress,
        referral_address: TonAddress,
        units: int,
        slippage_tolerance: float,
        swap_type: SwapType,
    ) -> TonSwapParams:

        dex_params_manager = DexParamsManager(config=self.config, ton_client=self.ton_client)

        params = await dex_params_manager.get_swap_params(
            offer_address=offer_address,
            ask_address=ask_address,
            referral_address=referral_address,
            units=units,
            slippage_tolerance=slippage_tolerance,
            swap_type=swap_type,
        )

        return params

    # === === === === === === ===

    async def get_provide_liquidity_params(
        self,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        slippage_tolerance: float,
        first_is_base: bool,
        account_address: TonAddress | None = None,
    ) -> TonBaseProvideLiquidityParams:

        dex_params_manager = DexParamsManager(config=self.config, ton_client=self.ton_client)

        params = await dex_params_manager.get_provide_liquidity_params(
            first_token_address=first_token_address,
            second_token_address=second_token_address,
            first_token_units=first_token_units,
            second_token_units=second_token_units,
            slippage_tolerance=slippage_tolerance,
            first_is_base=first_is_base,
            account_address=account_address,
        )

        return params

    # === === === === === === ===

    async def prepare_create_pool_transaction(
        self,
        account_address: TonAddress,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
    ) -> TonPreparedTransaction:

        router = TonDexRouterContract(
            address=self.config.ton_dex.router_address,
            ton_client=self.ton_client,
            config=self.config,
            proxy_ton_address=self.config.ton_dex.proxy_ton_address,
        )

        pool_address = await router.get_pool_address(
            token_0_address=first_token_address, token_1_address=second_token_address
        )

        if pool_address is None:
            raise PoolAddressNotFoundError()

        transaction_data = await router.prepare_provide_liquidity_transaction(
            account_address=account_address,
            token_address_0=first_token_address,
            token_address_1=second_token_address,
            amount_0=first_token_units,
            amount_1=second_token_units,
            min_lp_out_units=1,
        )

        send_ton_message = TonPreparedMessage(address=pool_address.to_string(), amount=500_000_000)
        transaction_data.messages.insert(0, send_ton_message)

        return transaction_data

    # === === === === === === ===

    async def prepare_provide_liquidity_transaction(
        self,
        account_address: TonAddress,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        min_lp_out_units: int,
    ) -> TonPreparedTransaction:

        router = TonDexRouterContract(
            address=self.config.ton_dex.router_address,
            ton_client=self.ton_client,
            config=self.config,
            proxy_ton_address=self.config.ton_dex.proxy_ton_address,
        )

        pool_address = await router.get_pool_address(
            token_0_address=first_token_address, token_1_address=second_token_address
        )
        if pool_address is None:
            raise PoolAddressNotFoundError()

        transaction_data = await router.prepare_provide_liquidity_transaction(
            account_address=account_address,
            token_address_0=first_token_address,
            token_address_1=second_token_address,
            amount_0=first_token_units,
            amount_1=second_token_units,
            min_lp_out_units=min_lp_out_units,
        )

        return transaction_data

    # === === === === === === ===

    async def prepare_provide_single_side_transaction(
        self,
        account_address: TonAddress,
        send_token_address: TonAddress,
        second_token_address: TonAddress,
        send_units: int,
        min_lp_out_units: int,
    ) -> TonPreparedTransaction:

        router = TonDexRouterContract(
            address=self.config.ton_dex.router_address,
            ton_client=self.ton_client,
            config=self.config,
            proxy_ton_address=self.config.ton_dex.proxy_ton_address,
        )

        pool_address = await router.get_pool_address(
            token_0_address=send_token_address, token_1_address=second_token_address
        )
        if pool_address is None:
            raise PoolAddressNotFoundError()

        transaction_data = await router.prepare_single_side_provide_liquidity_transaction(
            account_address=account_address,
            send_token_address=send_token_address,
            pair_token_address=second_token_address,
            send_units=send_units,
            min_lp_out_units=min_lp_out_units,
        )

        return transaction_data

    # === === === === === === ===

    async def prepare_activate_liquidity_transaction(
        self,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        min_lp_out_units: int,
        account_address: TonAddress,
    ) -> TonPreparedTransaction:

        router = TonDexRouterContract(
            address=self.config.ton_dex.router_address,
            ton_client=self.ton_client,
            config=self.config,
            proxy_ton_address=self.config.ton_dex.proxy_ton_address,
        )

        pool_address = await router.get_pool_address(
            token_0_address=first_token_address, token_1_address=second_token_address
        )
        if pool_address is None:
            raise PoolAddressNotFoundError()

        pool_contract = PoolContract(address=pool_address, ton_client=self.ton_client)
        lp_account_address = await pool_contract.get_lp_account_address(
            owner_address=account_address
        )

        if not lp_account_address:
            raise LpAccountAddressNotFoundError()

        lp_account_contract = LpAccountContract(
            address=lp_account_address, ton_client=self.ton_client, config=self.config
        )

        transaction_data = await lp_account_contract.prepare_activate_liquidity_transaction(
            first_token_units=first_token_units,
            second_token_units=second_token_units,
            min_lp_out_units=min_lp_out_units,
        )

        return transaction_data

    # === === === === === === ===

    async def prepare_refund_liquidity_transaction(
        self,
        account_address: TonAddress,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
    ) -> TonPreparedTransaction:

        router = TonDexRouterContract(
            address=self.config.ton_dex.router_address,
            ton_client=self.ton_client,
            config=self.config,
            proxy_ton_address=self.config.ton_dex.proxy_ton_address,
        )

        pool_address = await router.get_pool_address(
            token_0_address=first_token_address, token_1_address=second_token_address
        )
        if pool_address is None:
            raise PoolAddressNotFoundError()

        pool_contract = PoolContract(address=pool_address, ton_client=self.ton_client)
        lp_account_address = await pool_contract.get_lp_account_address(
            owner_address=account_address
        )

        if not lp_account_address:
            raise LpAccountAddressNotFoundError()

        lp_account_contract = LpAccountContract(
            address=lp_account_address, ton_client=self.ton_client, config=self.config
        )

        transaction_data = await lp_account_contract.prepare_refund_transaction()

        return transaction_data

    # === === === === === === ===

    async def prepare_burn_liquidity_transaction(
        self,
        account_address: TonAddress,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        lp_units: int,
    ) -> TonPreparedTransaction:

        router = TonDexRouterContract(
            address=self.config.ton_dex.router_address,
            ton_client=self.ton_client,
            config=self.config,
            proxy_ton_address=self.config.ton_dex.proxy_ton_address,
        )

        pool_address = await router.get_pool_address(
            token_0_address=first_token_address, token_1_address=second_token_address
        )

        if pool_address is None:
            raise PoolAddressNotFoundError()

        lp_wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=pool_address, owner_address=account_address
        )

        if not lp_wallet_address:
            raise LpWalletAddressNotFoundError()

        lp_wallet_contract = LpWalletContract(
            address=lp_wallet_address, ton_client=self.ton_client, config=self.config
        )
        transaction_data = await lp_wallet_contract.prepare_burn_liquidity_transaction(
            lp_units=lp_units
        )

        return transaction_data

    # === === === === === === ===

    def swap_proxy_to_ton_address(
        self,
        address: TonAddress,
    ) -> TonAddress:

        if address == self.config.ton_dex.proxy_ton_address:
            return TonConstants.ContractAddresses.TON

        return address

    # === === === === === === ===
