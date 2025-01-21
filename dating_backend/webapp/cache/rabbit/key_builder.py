from conf.config import settings


def get_user_search_queue_key(user_id: int) -> str:
    return f'{settings.RABBIT_MEET_USER_PREFIX}:user_search:{user_id}'


def get_liked_user_queue_key(user_id: int) -> str:
    return f'{settings.RABBIT_MEET_USER_PREFIX}:liked_user:{user_id}'
