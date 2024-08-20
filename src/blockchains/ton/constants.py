from dataclasses import dataclass

from src.utils.ton_address import TonAddress


@dataclass(frozen=True)
class TonConstants:
    MASTERCHAIN_ID = -1
    BASECHAIN_ID = 0

    @dataclass(frozen=True)
    class TonConnect:
        PREPARED_TRANSACTION_LIFETIME_MINUTES = 5

    @dataclass(frozen=True)
    class Fees:
        TON_TRANSFER_FEE = 10_000_000
        JETTON_TRANSFER_FEE = 50_000_000
        JETTON_TRANSFER_FORWARD_TON_AMOUNT = 1_000_000

        SWAP = 220_000_000
        SWAP_JETTON_TO_TON = 170_000_000
        SWAP_MIN = 65_000_000
        SWAP_FORWARD = 175_000_000
        SWAP_TON_TO_JETTON_FORWARD = 185_000_000
        SWAP_JETTON_TO_TON_FORWARD = 125_000_000
        PROVIDE_LP = 300_000_000
        PROVIDE_LP_TON_FORWARD = 265_000_000
        PROVIDE_LP_JETTON_FORWARD = 240_000_000
        BURN_LIQUIDITY = 500_000_000
        DIRECT_ADD_LP = 300_000_000
        REFUND = 300_000_000

    @dataclass(frozen=True)
    class ContractAddresses:
        TON = TonAddress("EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c")
        USDT = TonAddress("EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs")

    @dataclass(frozen=True)
    class OpCodes:
        COMMENT = 0x00000000
        JETTON_TRANSFER_NOTIFICATION = 0x7362D09C
        JETTON_TRANSFER = 0x0F8A7EA5
        EXCESS = 0xD53276DB

        JETTON_STAKE = 0x402EFF0B

        SWAP = 0x25938561
        PROVIDE_LIQUIDITY = 0xFCF9E58F
        DIRECT_ADD_LIQUIDITY = 0x4CF82803
        REFUND_ME = 0x0BF3F447
        BURN_LIQUIDITY = 0x595F07BC

        PAY_TO = 0xF93BB43F
