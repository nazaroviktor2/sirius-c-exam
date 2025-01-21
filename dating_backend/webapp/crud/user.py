from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from webapp.models.meet.search_params import SearchParams
from webapp.models.meet.user import User
from webapp.models.meet.statistics import Statistics
from webapp.schema.auth.register.user import UserRegister
from webapp.logger import logger


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return (
        await session.scalars(
            select(User).where(
                User.id == user_id
            )
        )
    ).one_or_none()


async def check_user(session: AsyncSession, user_id: int) -> bool:
    query = select(exists().where(User.id == user_id))
    return bool(await session.scalar(query))


async def create_user(session: AsyncSession, user_info: UserRegister) -> Optional[User]:
    try:
        user = User(
            id=user_info.id
        )
        statistics = Statistics(
            user_id=user_info.id
        )

        session.add(user)
        session.add(statistics)
        await session.commit()
        return user
    except Exception as err:
        logger.error(f'An error occurred while creating a user: {err}')
        await session.rollback()
        return None
