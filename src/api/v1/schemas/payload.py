from src.api.v1.schemas.base_messages import SuccessMessage


class PayloadResponse(SuccessMessage):

    payload: str
