from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.models.meet.search_params import SearchParams
from webapp.schema.search.search import SearchParamsUpdate


async def get_user_search_params(session: AsyncSession, user_id: int) -> Optional[SearchParams]:
    return (
        await session.scalars(
            select(SearchParams)
            .where(SearchParams.user_id == user_id)
        )
    ).one_or_none()


async def create_user_search_params(
    session: AsyncSession,
    user_id: int,
    search_info: SearchParamsUpdate
) -> Optional[SearchParams]:
    try:
        new_search = SearchParams(**search_info.model_dump())
        new_search.user_id = user_id

        session.add(new_search)
        await session.commit()

        return new_search
    except Exception as err:
        logger.error(f'An error occurred while creating search params: {err}')
        await session.rollback()
        return None


async def update_search_params(
    session: AsyncSession,
    search: SearchParams,
    updated_info: SearchParamsUpdate
) -> Optional[SearchParams]:
    try:
        for key, value in updated_info.model_dump(exclude_unset=True).items():
            setattr(search, key, value)
        await session.commit()
        return search
    except Exception as err:
        logger.error(f'An error occurred while updating search params: {err}')
        await session.rollback()
        raise None
