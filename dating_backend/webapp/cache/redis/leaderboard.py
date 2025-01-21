from typing import Optional, List, Any, Dict, Sequence

import orjson

from webapp.cache.redis.key_builder import (
    get_leaderboard_top_users_cache, get_leaderboard_users_cache
)
from webapp.db.redis import get_redis
from webapp.metrics import async_integrations_timer
from webapp.models.meet.leaderboard import Leaderboard


async def redis_set_leaderboard_top_users(
    payload: Dict[str, Any],
) -> None:
    redis = get_redis()
    redis_key = await get_leaderboard_top_users_cache()

    users = {
        orjson.dumps(user): user['rank']
        for user in payload.get('users', [])
    }

    await redis.zadd(redis_key, users)


async def redis_get_leaderboard_top_users(
    limit: int = 10
) -> Optional[List[Dict[str, Any]]]:
    redis = get_redis()

    redis_key = await get_leaderboard_top_users_cache()

    num_users = await redis.zcard(redis_key)
    if num_users < limit:
        return None

    cache = await redis.zrange(redis_key, 0, limit - 1, withscores=False)
    if cache is None:
        return []

    return [orjson.loads(user) for user in cache]


@async_integrations_timer
async def redis_get_leaderboard_user_data(
    user_id: int
) -> dict[str, str]:
    redis = get_redis()
    redis_key = await get_leaderboard_users_cache()

    cache = await redis.hget(redis_key, str(user_id))
    if cache is None:
        return {}

    return orjson.loads(cache)


@async_integrations_timer
async def redis_set_leaderboard_user_data(
    user_id: int, payload: Any
) -> None:
    redis = await get_redis()
    redis_key = await get_leaderboard_users_cache()

    await redis.hset(redis_key, str(user_id), orjson.dumps(payload))
