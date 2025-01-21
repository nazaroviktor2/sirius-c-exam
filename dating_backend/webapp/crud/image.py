from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.logger import logger
from webapp.models.meet.image import Image, ContentEnum


async def get_user_image(session: AsyncSession, user_id: int) -> Optional[Image]:
    return (
        await session.scalars(
            select(Image)
            .where(Image.user_id == user_id)
        )
    ).one_or_none()


async def create_user_image(
    session: AsyncSession,
    user_id: int,
    path: str,
    content_type: ContentEnum
) -> Optional[Image]:
    try:
        image = Image(
            user_id=user_id,
            path=path,
            content_type=content_type
        )

        session.add(image)
        await session.commit()

        return image
    except Exception as err:
        logger.error(f'An error occurred while creating the image: {err}')
        await session.rollback()
        raise err


async def update_user_image(
    session: AsyncSession,
    image: Image,
    path: str,
    content_type: ContentEnum
) -> Optional[Image]:
    try:
        image.path = path
        image.content_type = content_type
        await session.commit()

        return image
    except Exception as err:
        logger.error(f'An error occurred while updating the image: {err}')
        await session.rollback()
        raise err
