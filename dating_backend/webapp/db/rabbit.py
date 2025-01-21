from aio_pika import RobustChannel

channel: RobustChannel


def get_channel() -> RobustChannel:
    global channel

    return channel
