from pydantic import BeforeValidator
from pytoniq_core import Address
from typing_extensions import Annotated


# === === === === === === ===
class TonAddress:

    is_testnet: bool = False

    @classmethod
    def set_testnet(cls, is_testnet: bool):
        cls.is_testnet = is_testnet

    # === === === === === === ===
    def __init__(
        self,
        address: "str | Address | TonAddress",
    ):
        if isinstance(address, str):
            self._address = Address(address)
        elif isinstance(address, Address):
            self._address = address
        else:
            self._address = address._address

    # === === === === === === ===
    @property
    def str_address(self) -> str:

        return self._address.to_str(True, True, False, self.is_testnet)

    @property
    def str_bounceable_address(self) -> str:

        return self._address.to_str(True, True, True, self.is_testnet)

    @property
    def wc(self) -> int:

        return self._address.wc

    @property
    def hash_part(self) -> bytes:

        return self._address.hash_part

    @property
    def address(self) -> Address:

        return self._address

    # === === === === === === ===
    def to_string(
        self,
        user_friendly: bool = True,
        is_url_safe: bool = True,
        bounceable: bool = False,
    ) -> str:

        return self._address.to_str(user_friendly, is_url_safe, bounceable, self.is_testnet)

    # === === === === === === ===

    def to_raw_string(self) -> str:

        return self.to_string(user_friendly=False, is_url_safe=False, bounceable=False)

    # === === === === === === ===
    def __eq__(
        self,
        __value: "str | TonAddress",
    ) -> bool:
        if isinstance(__value, str):
            return self.str_address == TonAddress(__value).str_address

        if isinstance(__value, TonAddress):
            return self.str_address == __value.str_address

        return False

    # === === === === === === ===
    def __hash__(self) -> int:
        return hash(self.str_address)


# === === === === === === ===
def validate_address_res_str(address: str | Address) -> str:
    try:
        return Address(address).to_str(True, True, False)
    except Exception:
        raise ValueError(f"Invalid address: {address}")


# === === === === === === ===
def validate_address(address: str | Address | TonAddress) -> TonAddress:

    try:
        return TonAddress(address)
    except Exception as e:
        raise ValueError(f"Invalid address: {address}. Error: {e}")


# === === === === === === ===
def validate_address_or_none(address: str | Address | None) -> TonAddress | None:

    if address is None:
        return None
    return validate_address(address)


# === === === === === === ===
ValidatedAddress = Annotated[TonAddress, BeforeValidator(validate_address)]
ValidatedAddressOrNone = Annotated[TonAddress | None, BeforeValidator(validate_address_or_none)]


# === === === === === === ===
# def compare_addresses(
#     address0: str | Address,
#     address1: str | Address,
# ) -> bool:
#     if isinstance(address0, str):
#         address0 = Address(address0)
#     if isinstance(address1, str):
#         address1 = Address(address1)

#     return Address(address0) == Address(address1)
