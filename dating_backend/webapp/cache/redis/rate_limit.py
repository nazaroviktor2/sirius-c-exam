from datetime import timedelta
from functools import wraps
from typing import Callable

from webapp.cache.redis.key_builder import get_rate_limit_cache
from webapp.db.redis import get_redis
from webapp.logger import logger
from webapp.metrics import async_integrations_timer


def rate_limit(max_calls: int, period: timedelta):
    def decorator(func: Callable):
        @async_integrations_timer
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            if user_id is None:
                return None

            redis = get_redis()

            key = await get_rate_limit_cache(func.__name__, user_id)

            current_count = await redis.get(key)
            if current_count is not None and int(current_count) >= max_calls:
                logger.info(f'Rate limit exceeded: {func.__name__} user_id: {user_id}')
                return None

            if await redis.exists(key):
                await redis.incr(key)
            else:
                await redis.set(key, 1, ex=period)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
