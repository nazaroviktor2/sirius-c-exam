from fastapi import Depends, HTTPException
from fastapi.responses import Response, ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.form.router import form_router
from webapp.cache.redis.crud import redis_drop_model_key
from webapp.crud.form import get_user_form, update_form
from webapp.db.postgres import get_session
from webapp.models.meet.form import Form
from webapp.schema.form.form import FormUpdate, FormResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@form_router.put('/update')
async def form_update_handler(
    body: FormUpdate,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> Response:
    try:
        user_id = access_token.get('user_id')

        form_to_update = await get_user_form(session, user_id)
        if not form_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        updated_form = await update_form(session, form_to_update, body)
        if updated_form is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        await redis_drop_model_key(Form.__tablename__, form_to_update.user_id)

        return ORJSONResponse(
            content=FormResponse.model_validate(updated_form).model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while deletion the form: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
