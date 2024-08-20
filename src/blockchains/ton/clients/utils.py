from pytoniq_core import Address, Cell, ExternalAddress, begin_cell
from src.utils.str_tools import b64str_to_bytes, bytes_to_b64str
from src.utils.ton_address import TonAddress


def get_address_cell(address: TonAddress | Address | str) -> Cell:
    if isinstance(address, str):
        address = Address(address)
    if isinstance(address, TonAddress):
        address = address.address
    return begin_cell().store_address(address).end_cell()


def get_address_slice(address: TonAddress | Address | str) -> str:
    address_cell = get_address_cell(address)
    address_slice = bytes_to_b64str((address_cell).to_boc(False))

    return address_slice


def parse_address_from_cell(cell: Cell) -> TonAddress | None:
    slice = cell.begin_parse()

    address = slice.load_address()

    # NOTE - ExternalAddress is not supported for now.
    if isinstance(address, ExternalAddress):
        return None

    if not address:
        return None

    return TonAddress(address)


def parse_address_from_boc(boc: str) -> TonAddress | None:
    cell = Cell.one_from_boc(b64str_to_bytes(boc))
    return parse_address_from_cell(cell)


def parse_address_from_bytes(address_bytes: bytes) -> TonAddress | None:
    cell = Cell.one_from_boc(address_bytes)
    return parse_address_from_cell(cell)


def parse_address_from_cell_str(cell_str: str) -> TonAddress | None:
    cell = Cell.one_from_boc(cell_str)
    return parse_address_from_cell(cell)
