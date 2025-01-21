import atexit
from contextlib import asynccontextmanager
from typing import AsyncIterator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.metrics import metrics
from webapp.middleware.logger import LogServerMiddleware
from webapp.api.v1 import router as api_v1
from webapp.on_startup.logger import setup_logger
from webapp.on_startup.rabbit import start_rabbit
from webapp.on_startup.redis import start_redis

from conf.config import settings
from webapp.utils.materialized.refresh import refresh_materialized


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        LogServerMiddleware,
    )

    # CORS Middleware should be the last.
    # See https://github.com/tiangolo/fastapi/issues/1663 .
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def setup_routers(app: FastAPI) -> None:
    app.add_route('/metrics', metrics)

    app.include_router(router=api_v1.router)


async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        refresh_materialized,
        trigger=IntervalTrigger(minutes=5),
        id="refresh_materialized_view",
        replace_existing=True,
    )
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logger()
    await start_redis()
    await start_scheduler()
    await start_rabbit()
    print('START APP')
    yield
    print('END APP')


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)

    setup_middleware(app)
    setup_routers(app)

    return app
