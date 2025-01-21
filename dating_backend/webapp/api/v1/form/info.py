from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.form.router import form_router
from webapp.cache.redis.crud import redis_get_model, redis_set_model
from webapp.crud.form import get_user_form
from webapp.db.postgres import get_session
from webapp.models.meet.form import Form
from webapp.schema.form.form import FormResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@form_router.get("/info", response_model=FormResponse)
async def form_info_handler(
    user_id: int = None,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        if user_id is None:
            user_id = access_token.get('user_id')

        cached_form = await redis_get_model(Form.__tablename__, user_id)

        if cached_form:
            return ORJSONResponse(
                content=cached_form,
                status_code=status.HTTP_200_OK
            )

        form = await get_user_form(session, user_id)
        if not form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        response_model = FormResponse.model_validate(form).model_dump()
        await redis_set_model(Form.__tablename__, user_id, response_model)

        return ORJSONResponse(
            content=response_model,
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while receiving the form: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
