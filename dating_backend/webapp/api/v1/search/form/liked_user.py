from typing import Optional

import msgpack
from aio_pika.abc import AbstractRobustQueue
from aio_pika.exceptions import QueueEmpty
from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.search.form.router import search_form_router
from webapp.cache.rabbit.key_builder import get_liked_user_queue_key
from webapp.cache.redis.crud import redis_drop_need_notification
from webapp.crud.form import get_form
from webapp.db.postgres import get_session
from webapp.db.rabbit import get_channel
from webapp.models.meet.form import Form
from webapp.schema.form.form import FormResponse
from webapp.schema.search.search import SearchFormsResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@search_form_router.get('/liked', response_model=SearchFormsResponse)
async def search_get_liked_user_form_handler(
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
):
    user_id = access_token.get('user_id')

    channel = get_channel()
    queue_key = get_liked_user_queue_key(user_id)
    queue = await channel.declare_queue(
        queue_key, auto_delete=False, durable=True
    )

    form = await process_get_liked_user_form(session, queue)
    if form is None:
        await redis_drop_need_notification(user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return ORJSONResponse(
        content=FormResponse.model_validate(form).model_dump(),
        status_code=status.HTTP_200_OK,
    )


async def process_get_liked_user_form(
    session: AsyncSession, queue: AbstractRobustQueue
) -> Optional[Form]:
    while True:
        try:
            body = (await queue.get(timeout=3, no_ack=True)).body
        except QueueEmpty:
            return None

        form_id = msgpack.unpackb(body)['form_id']
        form = await get_form(session, form_id)

        if form is not None:
            return form
