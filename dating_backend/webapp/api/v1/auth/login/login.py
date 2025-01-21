from typing import Annotated

from fastapi import Depends, HTTPException, Header
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.auth.router import auth_router
from webapp.utils.auth.api_key import validate_and_check_api_key
from webapp.crud.user import get_user
from webapp.db.postgres import get_session
from webapp.schema.auth.login.user import UserLogin, UserLoginResponse
from webapp.utils.auth.jwt import jwt_auth
from webapp.logger import logger


@auth_router.post(
    '/login',
    response_model=UserLoginResponse,
)
async def auth_login_handler(
    body: UserLogin,
    authorization: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    try:
        valid_token = await validate_and_check_api_key(session, authorization)
        if not valid_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        user = await get_user(session, body.id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if user.is_banned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return ORJSONResponse(
            {
                'access_token': jwt_auth.create_token(user),
                'role': user.role.value
            }
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred during login: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
