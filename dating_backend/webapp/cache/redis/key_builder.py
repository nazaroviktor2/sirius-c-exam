from conf.config import settings


async def get_user_shown_form_cache(user_id: int) -> str:
    return f'{settings.REDIS_MEET_CACHE_PREFIX}:shown_form:{user_id}'


async def get_leaderboard_top_users_cache() -> str:
    return f'{settings.REDIS_MEET_CACHE_PREFIX}:top_users'


async def get_leaderboard_users_cache() -> str:
    return f'{settings.REDIS_MEET_CACHE_PREFIX}:users'


async def get_notification_cache(user_id: int) -> str:
    return f'{settings.REDIS_MEET_CACHE_PREFIX}:notify:{user_id}'


async def get_model_cache(model: str, user_id: int) -> str:
    return f"{settings.REDIS_MEET_CACHE_PREFIX}:{model}:{user_id}"


async def get_rate_limit_cache(func: str, user_id: int) -> str:
    return f"{settings.REDIS_MEET_CACHE_PREFIX}:rate_limit:{func}:{user_id}"
