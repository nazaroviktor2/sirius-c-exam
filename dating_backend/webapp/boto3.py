from typing import AsyncGenerator

from conf.config import settings

from botocore.client import Config
from aioboto3.session import Session
from types_aiobotocore_s3.client import S3Client


s3_conf = dict(
    service_name=settings.AWS_SERVICE_NAME,
    endpoint_url=settings.AWS_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
    config=Config(s3={'addressing_style': 'path'})
)

session = Session()


async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    async with session.client(**s3_conf) as s3_client:
        yield s3_client
