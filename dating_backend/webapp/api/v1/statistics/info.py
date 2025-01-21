from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.statistics.router import stats_router
from webapp.cache.redis.crud import redis_get_model, redis_set_model
from webapp.models.meet.statistics import Statistics
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.db.postgres import get_session
from webapp.schema.statistics.statistics import StatisticsResponse
from webapp.crud.statistics import get_user_statistics
from webapp.logger import logger


@stats_router.get(
    "/info",
    response_model=StatisticsResponse
)
async def stats_info_handler(
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        user_id = access_token.get("user_id")

        cached_stats = await redis_get_model(Statistics.__tablename__, user_id)

        if cached_stats:
            return ORJSONResponse(
                content=cached_stats,
                status_code=status.HTTP_200_OK
            )

        statistics = await get_user_statistics(session, user_id)

        if statistics is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        response_model = StatisticsResponse.model_validate(statistics).model_dump()
        await redis_set_model(Statistics.__tablename__, user_id, response_model)

        return ORJSONResponse(
            content=response_model,
            status_code=status.HTTP_200_OK
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while retrieving statistics: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
