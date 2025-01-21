from aio_pika import connect_robust

from conf.config import settings
from webapp.db import rabbit


async def start_rabbit():
    connection = await connect_robust(
        f'amqp://{settings.RABBIT_USER}:{settings.RABBIT_PASS}@rabbitmq/'
    )
    rabbit.channel = await connection.channel(publisher_confirms=False)
