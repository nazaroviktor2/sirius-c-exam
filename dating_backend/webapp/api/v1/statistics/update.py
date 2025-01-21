from fastapi import Depends, HTTPException
from fastapi.responses import Response, ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.statistics.router import stats_router
from webapp.cache.redis.crud import redis_drop_model_key
from webapp.crud.form import update_form
from webapp.crud.statistics import get_user_statistics, update_statistics
from webapp.db.postgres import get_session
from webapp.models.meet.statistics import Statistics
from webapp.schema.statistics.statistics import UpdateStatistics, StatisticsResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@stats_router.put('/update/{user_id}')
async def stats_update_handler(
    user_id: int,
    body: UpdateStatistics,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> Response:
    try:
        statistics_to_update = await get_user_statistics(session, user_id)

        if statistics_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        updated_statistics = await update_statistics(
            session, statistics_to_update, body
        )
        if updated_statistics is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        await redis_drop_model_key(Statistics.__tablename__, user_id)

        return ORJSONResponse(
            content=StatisticsResponse.model_validate(updated_statistics).model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while deletion the form: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
