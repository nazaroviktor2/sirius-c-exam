from typing import Optional

import msgpack
from aio_pika.abc import AbstractRobustQueue
from aio_pika.exceptions import QueueEmpty
from aio_pika import Message, RobustChannel
from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.search.form.router import search_form_router
from webapp.cache.rabbit.key_builder import get_user_search_queue_key
from webapp.cache.redis.crud import redis_add_shown_form, redis_get_shown_forms, redis_get_model
from webapp.crud.form import get_form, get_forms_by_search_params
from webapp.crud.search_params import get_user_search_params
from webapp.db.postgres import get_session
from webapp.db.rabbit import get_channel
from webapp.models.meet.form import Form
from webapp.models.meet.search_params import SearchParams
from webapp.schema.form.form import FormResponse
from webapp.schema.search.search import SearchFormsResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@search_form_router.get('/select', response_model=SearchFormsResponse)
async def search_select_form_handler(
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
):
    user_id = access_token.get('user_id')

    channel = get_channel()
    queue_key = get_user_search_queue_key(user_id)
    queue = await channel.declare_queue(
        queue_key, auto_delete=False, durable=True
    )

    form = await process_get_form(
        session, queue, channel,
        queue_key, user_id
    )
    if form is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await redis_add_shown_form(user_id, form.id)

    return ORJSONResponse(
        content=FormResponse.model_validate(form).model_dump(),
        status_code=status.HTTP_200_OK,
    )


async def process_get_form(
    session: AsyncSession,
    queue: AbstractRobustQueue,
    channel: RobustChannel,
    queue_key: str,
    user_id: int,
) -> Optional[Form]:
    form = await get_active_form_from_queue(session, queue)

    if form is None:
        shown_ids = await redis_get_shown_forms(user_id)

        forms = await get_forms_by_search_params(
            session=session,
            shown_ids=shown_ids,
            user_id=user_id
        )
        if not forms:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        for form_id in forms:
            await channel.default_exchange.publish(
                Message(
                    msgpack.packb({'form_id': form_id}),
                    content_type='text/plain'
                ),
                queue_key
            )

        form = await get_active_form_from_queue(session, queue)

    return form


async def get_active_form_from_queue(
    session: AsyncSession,
    queue: AbstractRobustQueue
) -> Optional[Form]:
    while True:
        try:
            message = await queue.get(timeout=3, no_ack=False)
            form_id = msgpack.unpackb(message.body)['form_id']

            form = await get_form(session, form_id)
            if form and form.is_active:
                await message.ack()
                return form
            else:
                await message.nack(requeue=False)

        except QueueEmpty:
            return None
