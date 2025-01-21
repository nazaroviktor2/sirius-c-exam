from os.path import splitext

from aioboto3 import Session
from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from types_aiobotocore_s3 import S3Client

from conf.config import settings
from webapp.api.v1.image.router import image_router
from webapp.boto3 import get_s3_client
from webapp.cache.redis.crud import redis_get_model, redis_set_model
from webapp.db.postgres import get_session
from webapp.crud.image import get_user_image
from webapp.models.meet.image import Image
from webapp.schema.image.image import ImageResponse
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth

from webapp.logger import logger


@image_router.get("/info/{user_id}")
async def image_info_handler(
    user_id: int,
    s3_client: S3Client = Depends(get_s3_client),
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    try:
        cached_user_image = await redis_get_model(
            Image.__tablename__, user_id
        )
        if cached_user_image:
            return ORJSONResponse(
                content=cached_user_image,
                status_code=status.HTTP_200_OK
            )

        user_image = await get_user_image(session, user_id)
        if user_image is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        url = await s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': user_image.path
            }
        )
        if url is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        response_model = ImageResponse(
            url=url, content_type=user_image.content_type
        ).model_dump()

        await redis_set_model(Image.__tablename__, user_id, response_model)

        return ORJSONResponse(
            content=response_model,
            status_code=status.HTTP_200_OK
        )
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while receiving images: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


ext_to_content_type = {
    'jpg': 'image/jpeg',
    'mp4': 'video/mp4'
}

