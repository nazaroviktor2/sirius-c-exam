from webapp.cache.redis.key_builder import get_leaderboard_top_users_cache, get_leaderboard_users_cache
from webapp.db.postgres import get_session
from sqlalchemy_utils.view import RefreshMaterializedView

from webapp.db.redis import get_redis
from webapp.models.meet.leaderboard import Leaderboard


async def refresh_materialized():
    async for session in get_session():
        await session.flush()
        await session.scalar(RefreshMaterializedView(
            name=Leaderboard.__tablename__,
            concurrently=False
        ))
        await session.commit()

    top_users_key = await get_leaderboard_top_users_cache()
    users_key = await get_leaderboard_users_cache()

    redis = get_redis()
    await redis.delete(top_users_key)
    await redis.delete(users_key)

