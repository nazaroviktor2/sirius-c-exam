from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from webapp.models.meet.api_key import ApiKey


async def check_api_key(session: AsyncSession, api_key: str) -> bool:
    query = select(
        exists()
        .where(ApiKey.key == api_key)
    )
    return bool(await session.scalar(query))
