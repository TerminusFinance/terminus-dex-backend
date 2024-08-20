from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.schemas import ErrorMessage
from src.api.v1.schemas.payload import PayloadResponse
from src.config import Config
from src.constants import ApiMessageCode
from src.dependencies.config import get_config
from src.dependencies.database_session import get_session
from src.exceptions import PayloadCreationError
from src.services import PayloadService


# === === === === === === ===
async def get_tonproof_payload(
    session: Annotated[AsyncSession, Depends(get_session)],
    config: Annotated[Config, Depends(get_config)],
) -> PayloadResponse | ErrorMessage:

    payload_service = PayloadService(session=session, config=config)
    try:
        payload = await payload_service.create_payload()
        await session.commit()
    except PayloadCreationError as e:
        await session.rollback()
        return ErrorMessage(code=ApiMessageCode.PAYLOAD_CREATION_FAILED, error=str(e))

    return PayloadResponse(payload=payload)
