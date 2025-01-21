from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.form.router import form_router
from webapp.crud.form import create_form, check_user_from_exists
from webapp.db.postgres import get_session
from webapp.schema.form.form import FormCreate, FormResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@form_router.post("/create", response_model=FormResponse)
async def form_create_handler(
    body: FormCreate,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        user_id = access_token.get('user_id')

        form_exists = await check_user_from_exists(
            session, user_id
        )
        if form_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        form = await create_form(session, user_id, body)
        if not form:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return ORJSONResponse(
            content=FormResponse.model_validate(form).model_dump(),
            status_code=status.HTTP_201_CREATED,
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while creating the form: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
