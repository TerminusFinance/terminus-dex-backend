from pydantic import BaseModel
from src.constants.api_message_code import ApiMessageCode


class Message(BaseModel):

    code: int


class ErrorMessage(Message):

    error: str


class SuccessMessage(Message):

    code: int = ApiMessageCode.SUCCESS
