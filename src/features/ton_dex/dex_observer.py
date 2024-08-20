# === === === === === === ===

from asyncio.locks import Lock
from typing import Dict, List, Set, cast

from sqlalchemy.ext.asyncio import AsyncSession
from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.constants import TonConstants
from src.blockchains.ton.schemas.ton_jetton_info import TonJettonInfo
from src.blockchains.ton.schemas.ton_transaction import TonTransaction
from src.config.config import Config
from src.database.repositories.storage_repo import StorageCellRepo
from src.database.repositories.ton.ton_asset_repository import TonAssetRepository
from src.database.repositories.ton.ton_dex_pool_repository import TonDexPoolRepository
from src.features.ton_common.jetton_wallet_contract import JettonWalletContract
from src.features.ton_common.schemas.ton_asset import TonAsset
from src.features.ton_dex.pool_contract import PoolContract
from src.utils.logging.logging import create_custom_logger
from src.utils.ton_address import TonAddress

# === === === === === === ===

logger = create_custom_logger("DexObserver")

# === === === === === === ===


class DexObserver:

    lock = Lock()

    # === === === === === === ===

    def __init__(
        self,
        config: Config,
        ton_client: TonClient,
        session: AsyncSession,
    ) -> None:

        self.config = config
        self.ton_client = ton_client
        self.session = session

    # === === === === === === ===
    async def update_pools(
        self,
    ):
        try:
            if DexObserver.lock.locked():
                print("DexObserver is already updating pools. Skipping...")
                return
            async with DexObserver.lock:
                await self._update_pools()
        except Exception as e:
            logger.exception(e)
            raise e

    # === === === === === === ===

    async def _update_pools(
        self,
    ):
        logger.info("Updating pools...")

        logger.info("Retrieving pools with activities...")
        pool_addresses = await self.find_pools()
        logger.info(
            "Found %d pools with activities. Pools:\n %s",
            len(pool_addresses),
            " ".join([address.to_string() for address in pool_addresses]),
        )

        if not pool_addresses:
            return

        logger.info("Retrieving all registered jettons...")
        jettons = await self.get_all_jettons()
        logger.info("Found %d jettons.", len(jettons))
        jettons_dict: Dict[TonAddress, TonJettonInfo] = {
            jetton.address: jetton for jetton in jettons
        }

        updated_assets = set()

        for pool_address in pool_addresses:
            try:
                await self.update_pool(
                    pool_address=pool_address,
                    jettons_dict=jettons_dict,
                    updated_assets=updated_assets,
                )
            except Exception as e:
                e.add_note(f"Pool updating: {pool_address.to_string()}")
                raise e

        await self.session.commit()
        logger.info("Updated %d pools and %d assets", len(pool_addresses), len(updated_assets))

    # === === === === === === ===

    async def update_pool(
        self,
        pool_address: TonAddress,
        jettons_dict: Dict[TonAddress, TonJettonInfo],
        updated_assets: Set[TonAddress],
    ) -> None:

        # === === === === === === ===

        pool_contract = PoolContract(address=pool_address, ton_client=self.ton_client)

        try:
            pool_data = await pool_contract.get_pool_data()
            if not pool_data:
                logger.info("Pool data not found: %s", pool_address.to_string())
                return
        except Exception as e:
            logger.warning("Pool data not found: %s. Error: %s", pool_address.to_string(), e)
            return
        try:
            pool_jetton_data = await pool_contract.get_jetton_data()
            if not pool_jetton_data:
                logger.info("Pool jetton data not found: %s", pool_address.to_string())
                return
        except Exception as e:
            logger.warning(
                "Pool jetton data not found: %s. Error: %s", pool_address.to_string(), e
            )
            return

        # === === === === === === ===

        first_wallet_contract = JettonWalletContract(
            address=pool_data.token_0_address, ton_client=self.ton_client
        )
        second_wallet_contract = JettonWalletContract(
            address=pool_data.token_1_address, ton_client=self.ton_client
        )

        try:
            first_jetton_wallet_data = await first_wallet_contract.get_wallet_data()
        except Exception as e:
            logger.warning(
                "Jetton wallet data not found: %s. Error: %s", pool_address.to_string(), e
            )
            return
        try:
            second_jetton_wallet_data = await second_wallet_contract.get_wallet_data()
        except Exception as e:
            logger.warning(
                "Jetton wallet data not found: %s. Error: %s", pool_address.to_string(), e
            )
            return

        if not first_jetton_wallet_data or not second_jetton_wallet_data:
            logger.info(
                "Jetton wallet data for pool %s not found(wallets): %s, %s",
                pool_address.to_string(),
                pool_data.token_0_address.to_string(),
                pool_data.token_1_address.to_string(),
            )
            return

        first_jetton = jettons_dict.get(first_jetton_wallet_data.jetton_contract_address, None)
        second_jetton = jettons_dict.get(second_jetton_wallet_data.jetton_contract_address, None)

        if not first_jetton or not second_jetton:
            logger.info(
                "Jettons for pool %s not found: %s, %s",
                pool_address.to_string(),
                pool_data.token_0_address.to_string(),
                pool_data.token_1_address.to_string(),
            )
            return
        # === === === === === === ===

        pool_repo = TonDexPoolRepository(session=self.session)
        asset_repo = TonAssetRepository(session=self.session)

        first_asset = TonAsset.from_jetton_info(first_jetton)
        second_asset = TonAsset.from_jetton_info(second_jetton)
        for asset in [first_asset, second_asset]:
            if asset.address in updated_assets:
                continue
            if await asset_repo.get(address=asset.address):
                await asset_repo.update(
                    address=asset.address,
                    image_url=asset.image_url,
                    decimals=asset.decimals,
                    symbol=asset.symbol,
                    name=asset.name,
                    is_blacklisted=asset.is_blacklisted,
                    is_community=asset.is_community,
                    is_deprecated=asset.is_deprecated,
                    is_whitelisted=asset.is_whitelisted,
                )
            else:
                await asset_repo.create(
                    address=asset.address,
                    symbol=asset.symbol,
                    name=asset.name,
                    image_url=asset.image_url,
                    decimals=asset.decimals,
                    is_community=asset.is_community,
                    is_deprecated=asset.is_deprecated,
                    is_blacklisted=asset.is_blacklisted,
                    is_whitelisted=asset.is_whitelisted,
                )
            updated_assets.add(asset.address)

        # === === === === === === ===
        if await pool_repo.get(address=pool_address):
            await pool_repo.update(
                address=pool_address,
                reserve_0=pool_data.reserve_0,
                reserve_1=pool_data.reserve_1,
                lp_fee=pool_data.lp_fee,
                protocol_fee=pool_data.protocol_fee,
                ref_fee=pool_data.ref_fee,
                collected_token_0_protocol_fee=pool_data.collected_token_0_protocol_fee,
                collected_token_1_protocol_fee=pool_data.collected_token_1_protocol_fee,
                total_supply=pool_jetton_data.total_supply,
            )
        else:
            await pool_repo.create(
                address=pool_address,
                reserve_0=pool_data.reserve_0,
                reserve_1=pool_data.reserve_1,
                token_0_wallet_address=pool_data.token_0_address,
                token_1_wallet_address=pool_data.token_1_address,
                token_0_minter_address=first_asset.address,
                token_1_minter_address=second_asset.address,
                lp_fee=pool_data.lp_fee,
                protocol_fee=pool_data.protocol_fee,
                ref_fee=pool_data.ref_fee,
                protocol_fee_address=pool_data.protocol_fee_address,
                collected_token_0_protocol_fee=pool_data.collected_token_0_protocol_fee,
                collected_token_1_protocol_fee=pool_data.collected_token_1_protocol_fee,
                total_supply=pool_jetton_data.total_supply,
            )

    async def find_pools(
        self,
    ) -> Set[TonAddress]:

        pools = set()

        storage_repo = StorageCellRepo(session=self.session)

        max_lt = cast(int | None, await storage_repo.get_value("max_lt", "int"))
        min_lt = cast(int | None, await storage_repo.get_value("min_lt", "int"))

        is_first_run = not max_lt and not min_lt

        has_transactions = True
        limit = 500
        while has_transactions:
            try:
                transactions = await self.get_router_transactions(
                    limit=limit,
                    before_lt=min_lt if is_first_run else None,
                    after_lt=max_lt if not is_first_run else None,
                )
                if limit < 500:
                    limit = min(500, limit * 2)
            except Exception as e:
                logger.error(e)
                if limit > 1:
                    limit = max(1, limit // 2)
                else:
                    raise e
                continue

            if not transactions:
                has_transactions = False
                continue

            for t in transactions:
                min_lt = min(min_lt, t.lt) if min_lt else t.lt
                max_lt = max(max_lt, t.lt) if max_lt else t.lt
            pools.update(await self.detect_pools_by_transactions(transactions=transactions))

        await storage_repo.set("max_lt", value=max_lt)
        await storage_repo.set("min_lt", value=min_lt)

        return pools

    # === === === === === === ===

    async def detect_pools_by_transactions(
        self,
        transactions: List[TonTransaction],
    ) -> Set[TonAddress]:

        pools = set()

        for transaction in transactions:
            in_msg = transaction.in_msg
            if in_msg and in_msg.op_code and in_msg.source:
                if in_msg.op_code == TonConstants.OpCodes.PAY_TO:
                    pools.add(in_msg.source)
                elif in_msg.op_code == TonConstants.OpCodes.JETTON_TRANSFER_NOTIFICATION:
                    if (
                        in_msg.decoded_body
                        and isinstance(in_msg.decoded_body, dict)
                        and "op_code" in in_msg.decoded_body
                    ):
                        try:
                            op_code = int(in_msg.decoded_body["op_code"], 16)
                        except Exception:
                            continue
                        if op_code in {
                            TonConstants.OpCodes.SWAP,
                            TonConstants.OpCodes.PROVIDE_LIQUIDITY,
                        }:
                            pools.add(in_msg.source.to_string())
            if transaction.out_msgs:
                for out_msg in transaction.out_msgs:
                    if (
                        out_msg.op_code == TonConstants.OpCodes.PROVIDE_LIQUIDITY
                        and out_msg.destination
                    ):
                        pools.add(out_msg.destination)

        return pools

    # === === === === === === ===

    async def get_router_transactions(
        self,
        limit: int = 100,
        before_lt: int | None = None,
        after_lt: int | None = None,
    ) -> List[TonTransaction]:

        router_address = self.config.ton_dex.router_address

        transactions = await self.ton_client.get_account_transactions(
            account_address=router_address, limit=limit, before_lt=before_lt, after_lt=after_lt
        )

        return transactions

    # === === === === === ===

    async def get_all_jettons(
        self,
    ) -> List[TonJettonInfo]:

        jettons = []

        limit = 1000
        offset = 0

        while True:
            next_jettons = await self.ton_client.get_all_jettons(limit=limit, offset=offset)
            offset += limit
            if not next_jettons:
                break
            jettons.extend(next_jettons)

        return jettons


# === === === === === === ===
