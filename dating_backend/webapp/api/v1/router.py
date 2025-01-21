from fastapi import APIRouter

from webapp.api.v1.auth.router import auth_router
from webapp.api.v1.form.router import form_router
from webapp.api.v1.image.router import image_router
from webapp.api.v1.notification.router import notification_router
from webapp.api.v1.search.router import search_router
from webapp.api.v1.statistics.router import stats_router
from webapp.api.v1.leaderboard.router import leaderboard_router

from conf.config import settings

router = APIRouter(prefix=settings.API_V1_STR)


router.include_router(auth_router, prefix='/auth', tags=['AUTH API'])
router.include_router(form_router, prefix='/form', tags=['FORM API'])
router.include_router(image_router, prefix='/image', tags=['IMAGE API'])
router.include_router(stats_router, prefix='/stats', tags=['STATS API'])
router.include_router(search_router, prefix='/search', tags=['SEARCH API'])
router.include_router(leaderboard_router, prefix='/leaderboard', tags=['LEADERBOARD API'])
router.include_router(notification_router, prefix='/notification', tags=['NOTIFICATION API'])
