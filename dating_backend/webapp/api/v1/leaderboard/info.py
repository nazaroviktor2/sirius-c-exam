from fastapi import Depends, HTTPException, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.leaderboard.router import leaderboard_router
from webapp.cache.redis.leaderboard import (
    redis_get_leaderboard_top_users, redis_set_leaderboard_top_users
)
from webapp.crud.leaderboard import get_leaderboard_top_users
from webapp.db.postgres import get_session
from webapp.schema.leaderboard.leaderboard import LeaderboardResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@leaderboard_router.get(
    "/info",
    response_model=LeaderboardResponse
)
async def leaderboard_info_handler(
    limit: int = Query(10, ge=10, le=100),
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        cached_leaderboard = await redis_get_leaderboard_top_users(
            limit=limit
        )
        if cached_leaderboard:
            return ORJSONResponse(
                content=cached_leaderboard,
                status_code=status.HTTP_200_OK
            )

        leaderboard = await get_leaderboard_top_users(session, limit)
        if leaderboard is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        response_model = LeaderboardResponse(users=leaderboard).model_dump()
        await redis_set_leaderboard_top_users(response_model)

        return ORJSONResponse(
            content=response_model,
            status_code=status.HTTP_200_OK
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while retrieving the leaderboard: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
