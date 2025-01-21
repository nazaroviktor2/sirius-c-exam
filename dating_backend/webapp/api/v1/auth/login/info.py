from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.auth.router import auth_router
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.db.postgres import get_session
from webapp.schema.auth.login.user import UserInfoResponse
from webapp.crud.user import get_user
from webapp.logger import logger


@auth_router.get(
    "/info",
    response_model=UserInfoResponse
)
async def auth_info_handler(
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        user_id = access_token.get("user_id")

        user = await get_user(session, user_id)

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return ORJSONResponse(
            content=UserInfoResponse.model_validate(user).model_dump(),
            status_code=status.HTTP_200_OK
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while verifying login information: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
