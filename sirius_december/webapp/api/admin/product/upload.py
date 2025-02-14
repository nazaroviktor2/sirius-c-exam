import asyncpg
from fastapi import Depends
from fastapi.responses import ORJSONResponse

from conf.config import settings
from webapp.api.admin.product.router import product_router
from webapp.models.meta import DEFAULT_SCHEMA
from webapp.schema.file.resize import ImageResize, ImageResizeResponse


@product_router.post('/upload', response_model=ImageResizeResponse)
async def upload_csv(
    body: ImageResize = Depends(),
    # access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        user=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    )

    buff = body.file.file
    buff.seek(0)

    columns = buff.readline().decode().strip().split(',')

    await conn.copy_to_table(
        'product', source=buff, schema_name=DEFAULT_SCHEMA,
        columns=columns, format='csv', header=False,
    )

    await conn.close()

    return ORJSONResponse(
        {
            'status': 'success'
        }
    )
