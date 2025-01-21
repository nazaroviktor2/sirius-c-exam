from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.models.meet.leaderboard import Leaderboard


async def get_leaderboard_user_data(
    session: AsyncSession, user_id: int
) -> Optional[Leaderboard]:
    return (
        await session.scalars(
            select(Leaderboard)
            .where(Leaderboard.user_id == user_id)
        )
    ).one_or_none()


async def get_leaderboard_top_users(
    session: AsyncSession,
    limit: int = 10,
) -> Optional[Sequence[Leaderboard]]:
    result = (await session.scalars(
        select(Leaderboard)
        .order_by(Leaderboard.rank)
        .limit(limit)
    )).all()

    if not result:
        return None

    return result
