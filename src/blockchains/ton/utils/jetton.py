from pytoniq_core.boc import Cell, begin_cell
from src.blockchains.ton.constants import TonConstants
from src.utils.str_tools import bytes_to_b64str
from src.utils.ton_address import TonAddress


# === === === === === === ===
def create_jetton_transfer_body(
    to_address: TonAddress,
    jetton_amount: int,
    forward_amount: int = 0,
    custom_payload: Cell | None = None,
    forward_payload: Cell | None = None,
    response_address: TonAddress | None = None,
    query_id: int = 0,
) -> Cell:

    # forward_payload_cell = (
    #     begin_cell().store_bytes(forward_payload).end_cell() if forward_payload else None
    # )
    # custom_payload_cell = (
    #     begin_cell().store_bytes(custom_payload).end_cell() if custom_payload else None
    # )

    cell_builder = (
        begin_cell()
        .store_uint(TonConstants.OpCodes.JETTON_TRANSFER, 32)
        .store_uint(query_id, 64)
        .store_coins(jetton_amount)
        .store_address(to_address.address)
        .store_address(response_address.address if response_address else to_address.address)
        .store_maybe_ref(custom_payload)
        .store_coins(forward_amount)
        .store_maybe_ref(forward_payload)
    )

    # if forward_payload:
    #     forward_payload_cell = begin_cell().store_bytes(forward_payload).end_cell()
    #     if cell_builder.available_bits > len(forward_payload_cell.bits):
    #         cell_builder.store_bit(0).store_cell(forward_payload_cell)
    #     else:
    #         cell_builder.store_bit(1).refs.append(forward_payload_cell)
    # else:
    #     cell_builder.store_bit(0)

    return cell_builder.end_cell()


# === === === === === === ===
def create_jetton_transfer_payload(
    to_address: TonAddress,
    jetton_amount: int,
    forward_amount: int = 0,
    custom_payload: Cell | None = None,
    forward_payload: Cell | None = None,
    response_address: TonAddress | None = None,
    query_id: int = 0,
) -> str:

    cell = create_jetton_transfer_body(
        to_address=to_address,
        jetton_amount=jetton_amount,
        forward_amount=forward_amount,
        custom_payload=custom_payload,
        forward_payload=forward_payload,
        response_address=response_address,
        query_id=query_id,
    )

    return bytes_to_b64str(cell.to_boc(False))
