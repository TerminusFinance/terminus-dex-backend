from typing import Literal, Tuple

from src.blockchains.ton.clients.ton_client import TonClient
from src.blockchains.ton.constants import TonConstants
from src.config.config import Config
from src.exceptions.ton_dex_exceptions import (
    LpAccountAddressNotFoundError,
    NotEnoughLiquidityError,
    PoolAddressNotFoundError,
    PoolNotFoundError,
)
from src.features.ton_dex.lp_account_contract import LpAccountContract
from src.features.ton_dex.pool_contract import PoolContract
from src.utils.ton_address import TonAddress

from .router_contract import TonDexRouterContract
from .schemas import (
    PoolData,
    TonBaseProvideLiquidityParams,
    TonCreateLiquidityPoolParams,
    TonProvideAction,
    TonProvideCommonParams,
    TonProvideLiquidityParams,
    TonSwapParams,
)

# === === === === === === ===

FEE_DIVIDER = 10000

# === === === === === === ===

type SwapType = Literal["direct", "reverse"]

# === === === === === === ===


class DexParamsManager:

    # === === === === === === ===

    def __init__(
        self,
        config: Config,
        ton_client: TonClient,
    ) -> None:

        self.config = config
        self.ton_client = ton_client
        self.router = TonDexRouterContract(
            ton_client=ton_client,
            config=self.config,
            address=config.ton_dex.router_address,
            proxy_ton_address=config.ton_dex.proxy_ton_address,
        )

    # === === === === === === ===

    async def get_swap_params(
        self,
        offer_address: TonAddress,
        ask_address: TonAddress,
        referral_address: TonAddress | None,
        units: int,
        slippage_tolerance: float,
        swap_type: SwapType,
    ) -> TonSwapParams:

        pool_data = await self._get_pool_data(
            token_0_address=offer_address, token_1_address=ask_address
        )

        if not pool_data:
            raise PoolNotFoundError()

        # pool_offer_wallet_address = await self._get_wallet_address(
        #     jetton_minter_address=offer_address, owner_address=pool_data.address
        # )
        # if not pool_offer_wallet_address:
        #     raise Exception("Pool offer wallet address not found.")

        in_reserved, out_reserved = (
            (pool_data.reserve_0, pool_data.reserve_1)
            # if pool_data.token_0_address == pool_offer_wallet_address
            if hash(offer_address.to_raw_string()) > hash(ask_address.to_raw_string())
            else (pool_data.reserve_1, pool_data.reserve_0)
        )

        if swap_type == "direct":
            result = await self.get_direct_swap_params(
                offer_address=offer_address,
                ask_address=ask_address,
                referral_address=referral_address,
                offer_units=units,
                slippage_tolerance=slippage_tolerance,
                in_reserved=in_reserved,
                out_reserved=out_reserved,
                pool_data=pool_data,
                pool_address=pool_data.address,
            )
        else:
            result = await self.get_reverse_swap_params(
                offer_address=offer_address,
                ask_address=ask_address,
                referral_address=referral_address,
                ask_units=units,
                slippage_tolerance=slippage_tolerance,
                in_reserved=in_reserved,
                out_reserved=out_reserved,
                pool_data=pool_data,
                pool_address=pool_data.address,
            )

        return result

    # === === === === === === ===

    async def get_direct_swap_params(
        self,
        offer_address: TonAddress,
        ask_address: TonAddress,
        referral_address: TonAddress | None,
        offer_units: int,
        slippage_tolerance: float,
        in_reserved: int,
        out_reserved: int,
        pool_data: PoolData,
        pool_address: TonAddress,
    ) -> TonSwapParams:

        ask_units, protocol_fee_units, ref_fee_units = _calculate_out_amount(
            has_ref=bool(referral_address),
            amount_in=offer_units,
            reserve_in=in_reserved,
            reserve_out=out_reserved,
            lp_fee=pool_data.lp_fee,
            protocol_fee=pool_data.protocol_fee,
            ref_fee=pool_data.ref_fee,
        )

        price_impact = _calculate_price_impact(
            amount=offer_units,
            reserved=in_reserved,
        )

        slippage_tolerance /= 100
        min_ask_units = int(ask_units * (1 - slippage_tolerance)) if ask_units > 0 else 0

        swap_rate = ask_units / offer_units if offer_units > 0 else 0

        fee_percent = (protocol_fee_units + ref_fee_units) / ask_units if ask_units > 0 else 0

        response = TonSwapParams(
            ask_address=ask_address,
            ask_units=ask_units,
            fee_address=ask_address,
            fee_percent=fee_percent,
            fee_units=int(protocol_fee_units + ref_fee_units),
            min_ask_units=min_ask_units,
            offer_address=offer_address,
            offer_units=offer_units,
            pool_address=pool_address,
            price_impact=price_impact,
            router_address=self.router.address,
            slippage_tolerance=slippage_tolerance,
            swap_rate=swap_rate,
            min_fee=TonConstants.Fees.SWAP_MIN,
            max_fee=self._get_swap_max_fee(
                offer_contract_address=offer_address, ask_contract_address=ask_address
            ),
        )

        return response

    # === === === === === === ===

    async def get_reverse_swap_params(
        self,
        offer_address: TonAddress,
        ask_address: TonAddress,
        referral_address: TonAddress | None,
        ask_units: int,
        slippage_tolerance: float,
        in_reserved: int,
        out_reserved: int,
        pool_data: PoolData,
        pool_address: TonAddress,
    ) -> TonSwapParams:

        if out_reserved < ask_units:
            raise NotEnoughLiquidityError()

        offer_units = _calculate_in_amount(
            has_ref=bool(referral_address),
            amount_out=ask_units,
            reserve_in=in_reserved,
            reserve_out=out_reserved,
            lp_fee=pool_data.lp_fee,
            protocol_fee=pool_data.protocol_fee,
            ref_fee=pool_data.ref_fee,
            slippage_tolerance=slippage_tolerance,
        )

        price_impact = _calculate_price_impact(
            amount=offer_units,
            reserved=in_reserved,
        )

        min_ask_units = ask_units
        swap_rate = (ask_units / offer_units) if offer_units > 0 else 0

        slippage_tolerance /= 100
        protocol_fee_units = (
            min_ask_units * (100 + slippage_tolerance) / (10_000 * pool_data.protocol_fee)
        )
        ref_fee_units = (
            (min_ask_units * (100 + slippage_tolerance) / (10_000 * pool_data.ref_fee))
            if referral_address
            else 0
        )
        fee_percent = (
            (protocol_fee_units + ref_fee_units) / min_ask_units * (100 + slippage_tolerance)
            if min_ask_units > 0
            else 0
        )

        response = TonSwapParams(
            ask_address=ask_address,
            ask_units=min_ask_units,
            fee_address=ask_address,
            fee_percent=fee_percent,
            fee_units=int(protocol_fee_units + ref_fee_units),
            min_ask_units=min_ask_units,
            offer_address=offer_address,
            offer_units=offer_units,
            pool_address=pool_address,
            price_impact=price_impact,
            router_address=self.router.address,
            slippage_tolerance=slippage_tolerance,
            swap_rate=swap_rate,
            min_fee=TonConstants.Fees.SWAP_MIN,
            max_fee=self._get_swap_max_fee(
                offer_contract_address=offer_address, ask_contract_address=ask_address
            ),
        )

        return response

    # === === === === === === ===

    async def get_provide_liquidity_params(
        self,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        first_is_base: bool,
        slippage_tolerance: float,
        account_address: TonAddress | None = None,
    ) -> TonBaseProvideLiquidityParams:

        pool_address = await self.router.get_pool_address(
            token_0_address=first_token_address, token_1_address=second_token_address
        )
        if not pool_address:
            raise PoolAddressNotFoundError()

        pool = PoolContract(address=pool_address, ton_client=self.ton_client)
        pool_data = await pool.get_pool_data()

        if not pool_data:
            # Pool not exists yet. Creating 'create' params.
            return await self._get_create_pool_params(
                first_token_address=first_token_address,
                second_token_address=second_token_address,
                first_token_units=first_token_units,
                second_token_units=second_token_units,
                pool_address=pool_address,
            )

        if account_address:
            lp_account_address = await pool.get_lp_account_address(owner_address=account_address)
            if not lp_account_address:
                raise LpAccountAddressNotFoundError()

            lp_account = LpAccountContract(
                address=lp_account_address, ton_client=self.ton_client, config=self.config
            )
            lp_account_data = await lp_account.get_lp_account_data()
        else:
            lp_account_address = None
            lp_account_data = None

        # === === === === === === ===

        if not lp_account_data or (
            lp_account_data.token_0_balance == 0 and lp_account_data.token_1_balance == 0
        ):
            # Account don't have lp tokens and tokens balances. Creating 'provide' params.
            return await self._get_simple_provide_params(
                first_token_address=first_token_address,
                second_token_address=second_token_address,
                first_token_units=first_token_units,
                second_token_units=second_token_units,
                slippage_tolerance=slippage_tolerance,
                first_is_base=first_is_base,
                pool=pool,
                lp_account_address=lp_account_address,
                pool_data=pool_data,
            )

        # pool_first_token_wallet_address = await self._get_wallet_address(
        #     jetton_minter_address=first_token_address,
        #     owner_address=pool_data.address,
        # )

        (
            first_token_reserved,
            second_token_reserved,
            first_token_balance,
            second_token_balance,
        ) = (
            (
                pool_data.reserve_0,
                pool_data.reserve_1,
                lp_account_data.token_0_balance,
                lp_account_data.token_1_balance,
            )
            # if pool_data.token_0_wallet_address == pool_first_token_wallet_address
            if hash(first_token_address.to_raw_string())
            > hash(second_token_address.to_raw_string())
            else (
                pool_data.reserve_1,
                pool_data.reserve_0,
                lp_account_data.token_1_balance,
                lp_account_data.token_0_balance,
            )
        )

        # === === === === === === ===

        send_token_address_r = None
        send_units_r = None
        action_r: TonProvideAction = TonProvideAction.PROVIDE

        if (first_token_balance > 0) ^ (second_token_balance > 0):
            # Need to provide second token.
            if first_token_balance != 0:
                first_token_units_r = int(
                    second_token_balance * (first_token_reserved / second_token_reserved)
                )
                second_token_units_r = second_token_balance
                send_token_address_r = first_token_address
            else:
                second_token_units_r = int(
                    first_token_balance * (second_token_reserved / first_token_reserved)
                )
                first_token_units_r = first_token_balance
                send_token_address_r = second_token_address
            action_r = TonProvideAction.PROVIDE_SECOND

        else:
            old_rate = first_token_balance / second_token_balance
            new_rate = first_token_reserved / second_token_reserved
            rate_delta_percent = 100 - min(old_rate, new_rate) / max(old_rate, new_rate) * 100
            if rate_delta_percent > slippage_tolerance:
                # Rate was changed. Need to provide additional tokens.
                if new_rate > old_rate:
                    first_token_units_r = int(second_token_balance * new_rate)
                    second_token_units_r = second_token_balance
                    send_token_address_r = first_token_address
                    send_units_r = first_token_units_r - first_token_balance
                else:
                    first_token_units_r = first_token_balance
                    second_token_units_r = int(first_token_balance / new_rate)
                    send_token_address_r = second_token_address
                    send_units_r = second_token_units_r - second_token_balance
                action_r = TonProvideAction.PROVIDE_ADDITIONAL

            else:
                # Need to activate provided liquidity.
                first_token_units_r = first_token_balance
                second_token_units_r = second_token_balance
                action_r = TonProvideAction.PROVIDE_DIRECT

        # === === === === === === ===

        common_params = await self._get_provide_common_params(
            pool=pool,
            first_token_address=first_token_address,
            second_token_address=second_token_address,
            first_token_units=first_token_units_r,
            second_token_units=second_token_units_r,
            first_token_reserved=first_token_reserved,
            second_token_reserved=second_token_reserved,
            slippage_tolerance=slippage_tolerance,
            first_is_base=first_is_base,
        )

        return TonProvideLiquidityParams(
            first_token_address=first_token_address,
            second_token_address=second_token_address,
            first_token_units=first_token_units_r,
            second_token_units=second_token_units_r,
            first_token_balance=first_token_balance,
            second_token_balance=second_token_balance,
            expected_lp_units=common_params.expected_lp_units,
            min_expected_lp_units=common_params.min_expected_lp_units,
            estimated_share_of_pool=common_params.estimated_share_of_pool,
            send_units=send_units_r,
            send_token_address=send_token_address_r,
            action=action_r,
            pool_address=pool_data.address,
            lp_account_address=lp_account.address,
            slippage_tolerance=slippage_tolerance,
            fee_min=150_000_000,
            fee_max=300_000_000,
        )

    # === === === === === === ===

    async def _get_pool_data(
        self,
        token_0_address: TonAddress,
        token_1_address: TonAddress,
    ) -> PoolData | None:

        pool_address = await self.router.get_pool_address(
            token_0_address=token_0_address, token_1_address=token_1_address
        )
        if not pool_address:
            raise PoolAddressNotFoundError()

        pool = PoolContract(address=pool_address, ton_client=self.ton_client)
        pool_data = await pool.get_pool_data()

        return pool_data

    # === === === === === === ===

    async def _get_create_pool_params(
        self,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        pool_address: TonAddress,
    ) -> TonCreateLiquidityPoolParams:

        if first_token_units == 0 or second_token_units == 0:
            pass
        elif first_token_units < second_token_units:
            second_token_units = int(second_token_units / first_token_units * 1001)
            first_token_units = 1001
        else:
            first_token_units = int(first_token_units / second_token_units * 1001)
            second_token_units = 1001

        params = TonCreateLiquidityPoolParams(
            first_token_address=first_token_address,
            second_token_address=second_token_address,
            first_token_units=first_token_units,
            second_token_units=second_token_units,
            pool_address=pool_address,
            fee_min=300_000_000,  # TODO: Remove hardcode
            fee_max=3_000_000_000,  # TODO: Remove hardcode
        )

        return params

    # === === === === === === ===

    async def _get_simple_provide_params(
        self,
        pool: PoolContract,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        first_is_base: bool,
        slippage_tolerance: float,
        pool_data: PoolData,
        lp_account_address: TonAddress | None = None,
    ) -> TonProvideLiquidityParams:

        # pool_first_token_wallet_address = await self._get_wallet_address(
        #     jetton_minter_address=first_token_address, owner_address=pool_data.address
        # )
        (first_token_reserved, second_token_reserved) = (
            (pool_data.reserve_0, pool_data.reserve_1)
            # if pool_data.token_0_wallet_address == pool_first_token_wallet_address
            if hash(first_token_address.to_raw_string())
            > hash(second_token_address.to_raw_string())
            else (pool_data.reserve_1, pool_data.reserve_0)
        )

        common_params = await self._get_provide_common_params(
            pool=pool,
            first_token_address=first_token_address,
            second_token_address=second_token_address,
            first_token_units=first_token_units,
            second_token_units=second_token_units,
            slippage_tolerance=slippage_tolerance,
            first_token_reserved=first_token_reserved,
            second_token_reserved=second_token_reserved,
            first_is_base=first_is_base,
        )

        params = TonProvideLiquidityParams(
            action=TonProvideAction.PROVIDE,
            first_token_address=first_token_address,
            second_token_address=second_token_address,
            first_token_units=common_params.first_token_units,
            second_token_units=common_params.second_token_units,
            slippage_tolerance=slippage_tolerance,
            expected_lp_units=common_params.expected_lp_units,
            min_expected_lp_units=common_params.min_expected_lp_units,
            estimated_share_of_pool=common_params.estimated_share_of_pool,
            pool_address=pool_data.address,
            lp_account_address=lp_account_address,
            fee_min=300_000_000,
            fee_max=600_000_000,
        )

        return params

    # === === === === === === ===

    async def _get_provide_common_params(
        self,
        pool: PoolContract,
        first_token_address: TonAddress,
        second_token_address: TonAddress,
        first_token_units: int,
        second_token_units: int,
        slippage_tolerance: float,
        first_token_reserved: int,
        second_token_reserved: int,
        first_is_base: bool,
    ):

        if first_is_base:
            second_token_units = int(
                first_token_units * (second_token_reserved / first_token_reserved)
            )
        else:
            first_token_units = int(
                second_token_units * (first_token_reserved / second_token_reserved)
            )

        estimated_share_of_pool = (
            round(first_token_units / (first_token_reserved + first_token_units), 4) * 100
        )

        first_token_units_t, second_token_units_t = (
            (first_token_units, second_token_units)
            if hash(first_token_address.to_raw_string())
            > hash(second_token_address.to_raw_string())
            else (second_token_units, first_token_units)
        )

        # TODO: Modify contract to send total supply in 'get_pool_data'
        #       and calculate expected units here
        expected_units = await pool.get_expected_lp_tokens(
            token_0_amount=first_token_units_t,
            token_1_amount=second_token_units_t,
        )
        if not expected_units:
            raise PoolNotFoundError()

        min_expected_tokens = int(expected_units * (100 - slippage_tolerance) / 100)

        return TonProvideCommonParams(
            first_token_units=first_token_units,
            second_token_units=second_token_units,
            expected_lp_units=expected_units,
            slippage_tolerance=slippage_tolerance,
            min_expected_lp_units=min_expected_tokens,
            estimated_share_of_pool=estimated_share_of_pool,
        )

    # === === === === === === ===
    def _get_swap_max_fee(
        self,
        offer_contract_address: TonAddress,
        ask_contract_address: TonAddress,
    ) -> int:

        if (
            offer_contract_address != TonConstants.ContractAddresses.TON
            and ask_contract_address != TonConstants.ContractAddresses.TON
        ):
            return TonConstants.Fees.SWAP

        elif offer_contract_address == TonConstants.ContractAddresses.TON:
            return TonConstants.Fees.SWAP_TON_TO_JETTON_FORWARD

        else:
            return TonConstants.Fees.SWAP_JETTON_TO_TON

    # === === === === === === ===

    async def _get_wallet_address(
        self,
        jetton_minter_address: TonAddress,
        owner_address: TonAddress,
    ) -> TonAddress:

        wallet_address = await self.ton_client.get_jetton_wallet_address(
            jetton_minter_address=(
                jetton_minter_address
                if jetton_minter_address != TonConstants.ContractAddresses.TON
                else self.config.ton_dex.proxy_ton_address
            ),
            owner_address=owner_address,
        )

        return wallet_address

    # === === === === === === ===


def _calculate_out_amount(
    has_ref: int,
    amount_in: int,
    reserve_in: int,
    reserve_out: int,
    lp_fee: int,
    protocol_fee: int,
    ref_fee: int,
) -> Tuple[int, int, int]:
    # TODO: Refactor

    if amount_in <= 0:
        return (0, 0, 0)

    amount_in_with_fee = amount_in / 1_000_000_000 * (FEE_DIVIDER - lp_fee)
    base_out = (amount_in_with_fee * reserve_out / 1_000_000_000) / (
        reserve_in / 1_000_000_000 * FEE_DIVIDER + amount_in_with_fee
    )

    protocol_fee_out = 0
    ref_fee_out = 0

    if protocol_fee > 0:
        protocol_fee_out = base_out * protocol_fee / FEE_DIVIDER

    if has_ref and (ref_fee > 0):
        ref_fee_out = base_out * ref_fee / FEE_DIVIDER

    base_out -= protocol_fee_out + ref_fee_out

    return (
        int(base_out * 1_000_000_000),
        int(protocol_fee_out * 1_000_000_000),
        int(ref_fee_out * 1_000_000_000),
    )


# === === === === === === ===


def _calculate_in_amount(
    has_ref: int,
    amount_out: int,
    reserve_in: int,
    reserve_out: int,
    lp_fee: int,
    protocol_fee: int,
    ref_fee: int,
    slippage_tolerance: float,
) -> int:

    if amount_out <= 0:
        return 0

    numerator = (
        ((reserve_in / 1_000_000_000) * (amount_out / 1_000_000_000)) * 10_000 * 1_000_000_000
    )
    denominator = (reserve_out - amount_out) / 1_000_000_000 * (10_000 - lp_fee)

    amount_in = numerator / denominator + 1

    amount_in = int((amount_in * (10_020 + (slippage_tolerance * 100))) // 10_000)

    return amount_in


# === === === === === === ===


def _calculate_price_impact(
    amount: int,
    reserved: int,
):
    # TODO: Refactor

    price_impact = amount / (reserved + amount) * 100
    return price_impact


# === === === === === === ===
