from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.search.params.router import search_params_router
from webapp.crud.search_params import get_user_search_params, create_user_search_params
from webapp.db.postgres import get_session
from webapp.schema.search.search import SearchParamsUpdate, SearchParamsResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@search_params_router.post(
    "/create",
    response_model=SearchParamsResponse
)
async def search_params_create_handler(
    body: SearchParamsUpdate,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        user_id = access_token.get('user_id')

        search_params_exists = await get_user_search_params(
            session, user_id
        )
        if search_params_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        search_params = await create_user_search_params(session, user_id, body)
        if not search_params:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return ORJSONResponse(
            content=SearchParamsResponse.model_validate(
                search_params
            ).model_dump(),
            status_code=status.HTTP_201_CREATED,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while creating the search: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
