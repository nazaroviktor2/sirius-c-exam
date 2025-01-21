from webapp.api.v1.search.params.router import search_params_router

from fastapi import Depends, HTTPException
from fastapi.responses import Response, ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.cache.rabbit.key_builder import get_user_search_queue_key
from webapp.cache.redis.crud import redis_drop_model_key
from webapp.db.postgres import get_session
from webapp.crud.search_params import get_user_search_params, update_search_params
from webapp.db.rabbit import get_channel
from webapp.models.meet.search_params import SearchParams
from webapp.schema.search.search import SearchParamsResponse, SearchParamsUpdate
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@search_params_router.put('/update')
async def update_search_params_handler(
    body: SearchParamsUpdate,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> Response:
    try:
        user_id = access_token.get('user_id')

        search_to_update = await get_user_search_params(session, user_id)
        if search_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        updated_search = await update_search_params(session, search_to_update, body)
        if updated_search is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        channel = get_channel()
        queue_key = get_user_search_queue_key(user_id)
        await channel.queue_delete(queue_key)

        await redis_drop_model_key(SearchParams.__tablename__, user_id)

        return ORJSONResponse(
            content=SearchParamsResponse.model_validate(updated_search).model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while updating the search: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
