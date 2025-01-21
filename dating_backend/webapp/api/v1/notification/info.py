from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from starlette import status

from webapp.api.v1.notification.router import notification_router
from webapp.cache.redis.crud import redis_get_need_notification
from webapp.schema.notification.notification import NotificationResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.logger import logger


@notification_router.get(
    "/is_notified",
    response_model=NotificationResponse
)
async def notification_info_handler(
    user_id: int,
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        is_notified = await redis_get_need_notification(user_id)

        return ORJSONResponse(
            content=NotificationResponse(is_notified=is_notified).model_dump(),
            status_code=status.HTTP_200_OK,
        )
    except Exception as err:
        logger.error(f'Error while retrieving notification information: {err}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
