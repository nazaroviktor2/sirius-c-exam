from typing import Annotated
from uuid import UUID

from fastapi import Header
from webapp.crud.api_key import check_api_key

from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger


async def validate_and_check_api_key(
    session: AsyncSession,
    authorization: Annotated[str, Header()]
) -> bool:
    try:
        _, token = authorization.split()
        UUID(token)  # validation
        return await check_api_key(session, token)
    except Exception as err:
        logger.error(f'Error validating API key: {err}')
        return False
