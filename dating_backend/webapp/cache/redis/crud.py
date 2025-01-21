from typing import Any, List, Optional

import orjson

from conf.config import settings
from webapp.cache.redis.key_builder import (
    get_user_shown_form_cache, get_model_cache,
    get_notification_cache
)
from webapp.db.redis import get_redis
from webapp.metrics import async_integrations_timer


@async_integrations_timer
async def redis_add_shown_form(user_id: int, form_id: int):
    redis = get_redis()
    key = await get_user_shown_form_cache(user_id)
    await redis.sadd(key, form_id)

    ttl = await redis.ttl(key)
    if ttl == -1:
        await redis.expire(key, settings.SHOWN_IDS_EXPIRE_TIME)


@async_integrations_timer
async def redis_get_need_notification(user_id: int) -> bool:
    redis = get_redis()
    key = await get_notification_cache(user_id)
    cache = await redis.get(key)
    return cache is None


@async_integrations_timer
async def redis_set_need_notification(user_id: int) -> None:
    redis = await get_redis()
    key = await get_notification_cache(user_id)
    await redis.set(key, 1, ex=settings.SHOWN_IDS_EXPIRE_TIME)


@async_integrations_timer
async def redis_drop_need_notification(user_id: int) -> None:
    redis = await get_redis()
    key = await get_notification_cache(user_id)
    await redis.delete(key)


@async_integrations_timer
async def redis_get_shown_forms(user_id: int) -> Optional[List[int]]:
    redis = get_redis()
    key = await get_user_shown_form_cache(user_id)
    shown_ids = await redis.smembers(key)
    if shown_ids:
        return [int(form_id) for form_id in shown_ids]

    return None


@async_integrations_timer
async def redis_set_model(model: str, model_id: int, payload: Any) -> None:
    redis = get_redis()
    redis_key = await get_model_cache(model, model_id)
    await redis.set(redis_key, orjson.dumps(payload), ex=settings.FILE_EXPIRE_TIME)


@async_integrations_timer
async def redis_get_model(model: str, model_id: int) -> dict[str, str]:
    redis = get_redis()
    redis_key = await get_model_cache(model, model_id)
    cache = await redis.get(redis_key)
    if cache is None:
        return {}
    return orjson.loads(cache)


@async_integrations_timer
async def redis_drop_model_key(model: str, model_id: int) -> None:
    redis = get_redis()
    redis_key = await get_model_cache(model, model_id)
    await redis.delete(redis_key)
