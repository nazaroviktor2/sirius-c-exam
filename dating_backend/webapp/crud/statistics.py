from typing import Optional, Sequence, Dict

from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.models.meet.statistics import Statistics
from webapp.schema.statistics.statistics import UpdateStatistics


async def get_user_statistics(session: AsyncSession, user_id: int) -> Optional[Statistics]:
    return (
        await session.scalars(
            select(Statistics)
            .where(Statistics.user_id == user_id)
        )
    ).one_or_none()


async def get_stats_for_leaderboard(
    session: AsyncSession
) -> Optional[Dict[str, int]]:
    result = (await session.scalars(
        select(Statistics)
    )).all()
    if not result:
        return None

    return {
        f'{user.user_id}': user.likes for user in result
    }


async def update_statistics(
        session: AsyncSession,
        statistics: Statistics,
        updated_info: UpdateStatistics
) -> Optional[Statistics]:
    try:
        for key, value in updated_info.model_dump(exclude_unset=True).items():
            current_value = getattr(statistics, key, 0)
            setattr(statistics, key, current_value + value)
        await session.commit()
        return statistics
    except Exception as err:
        logger.error(f'An error occurred while updating statistics: {err}')
        await session.rollback()
        raise None
