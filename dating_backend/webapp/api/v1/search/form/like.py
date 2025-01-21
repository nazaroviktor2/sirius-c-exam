import msgpack
from aio_pika import Message
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.v1.search.form.router import search_form_router
from webapp.cache.rabbit.key_builder import get_liked_user_queue_key
from webapp.cache.redis.crud import redis_set_need_notification, redis_get_need_notification
from webapp.crud.form import get_user_form
from webapp.db.postgres import get_session
from webapp.db.rabbit import get_channel
from webapp.schema.search.search import SearchFormsResponse, SearchLike
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@search_form_router.post('/like', response_model=SearchFormsResponse)
async def search_like_user_form_handler(
    body: SearchLike,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
):
    user_form = await get_user_form(
        session, access_token.get('user_id')
    )
    if user_form is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    channel = get_channel()
    queue_key = get_liked_user_queue_key(body.user_id)

    await channel.declare_queue(
        queue_key, auto_delete=False, durable=True
    )

    await channel.default_exchange.publish(
        Message(
            msgpack.packb({'form_id': user_form.id}),
            content_type='text/plain'
        ),
        queue_key
    )

    is_notified = await redis_get_need_notification(body.user_id)
    if is_notified:
        await redis_set_need_notification(body.user_id)

    return Response(status_code=status.HTTP_201_CREATED)
