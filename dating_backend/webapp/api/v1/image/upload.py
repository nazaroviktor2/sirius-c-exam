from fastapi import Depends, HTTPException, UploadFile
from uuid import uuid4

from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from types_aiobotocore_s3 import S3Client

from webapp.api.v1.image.router import image_router
from webapp.cache.redis.crud import redis_drop_model_key
from webapp.crud.image import get_user_image, create_user_image, update_user_image
from webapp.db.postgres import get_session
from webapp.models.meet.image import ContentEnum, Image
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth
from webapp.boto3 import get_s3_client
from webapp.logger import logger

from conf.config import settings
from webapp.utils.image.const import jpeg_start_bytes


@image_router.post("/upload")
async def upload_image_handler(
    image: UploadFile,
    s3_client: S3Client = Depends(get_s3_client),
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> Response:
    try:
        user_id = access_token.get('user_id')

        file = await image.read()
        if file.startswith(jpeg_start_bytes):
            key = f'images/{user_id}/{uuid4()}.jpg'
            content_type = ContentEnum.photo
        else:
            key = f'images/{user_id}/{uuid4()}.mp4'
            content_type = ContentEnum.video

        await s3_client.put_object(
            Body=file,
            Bucket=settings.AWS_BUCKET_NAME,
            Key=key
        )

        user_image = await get_user_image(session, user_id)

        if user_image is None:
            user_image = await create_user_image(
                session, user_id, key, content_type
            )
            if user_image is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                await s3_client.delete_object(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=user_image.path
                )
            except Exception as err:
                logger.error(f'Failed to delete image in S3: {err}')

            user_image = await update_user_image(
                session, user_image, key, content_type
            )
            if user_image is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        await redis_drop_model_key(Image.__tablename__, user_id)

        return Response(status_code=status.HTTP_200_OK)
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f'An error occurred while uploading the image: {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
