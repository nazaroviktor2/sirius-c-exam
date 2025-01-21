from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.search.params.router import search_params_router
from webapp.cache.redis.crud import redis_get_model, redis_set_model
from webapp.crud.search_params import get_user_search_params
from webapp.db.postgres import get_session
from webapp.models.meet.search_params import SearchParams
from webapp.schema.search.search import SearchParamsResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@search_params_router.get("/info", response_model=SearchParamsResponse)
async def search_params_info_handler(
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        user_id = access_token.get('user_id')

        cached_search_params = await redis_get_model(
            SearchParams.__tablename__, user_id
        )
        if cached_search_params:
            return ORJSONResponse(
                content=cached_search_params,
                status_code=status.HTTP_200_OK
            )

        search_params = await get_user_search_params(session, user_id)
        if search_params is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        response_model = SearchParamsResponse.model_validate(search_params).model_dump()
        await redis_set_model(SearchParams.__tablename__, user_id, response_model)

        return ORJSONResponse(
            content=response_model,
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while receiving the search: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
