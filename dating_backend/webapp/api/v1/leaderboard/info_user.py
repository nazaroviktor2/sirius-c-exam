from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.leaderboard.router import leaderboard_router
from webapp.cache.redis.leaderboard import (
    redis_get_leaderboard_user_data,
    redis_set_leaderboard_user_data
)
from webapp.crud.leaderboard import get_leaderboard_user_data
from webapp.db.postgres import get_session
from webapp.schema.leaderboard.leaderboard import UserData
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@leaderboard_router.get(
    "/user_info",
    response_model=UserData
)
async def leaderboard_info_user_handler(
    user_id: int = None,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        if user_id is None:
            user_id = access_token.get('user_id')

        cached_user_data = await redis_get_leaderboard_user_data(
            user_id=user_id
        )
        if cached_user_data:
            return ORJSONResponse(
                content=cached_user_data,
                status_code=status.HTTP_200_OK
            )

        leaderboard = await get_leaderboard_user_data(
            session=session, user_id=user_id
        )
        if leaderboard is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        response_model = UserData.model_validate(leaderboard).model_dump()
        await redis_set_leaderboard_user_data(
            user_id=user_id, payload=response_model
        )

        return ORJSONResponse(
            content=response_model,
            status_code=status.HTTP_200_OK
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while retrieving the leaderboard: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
