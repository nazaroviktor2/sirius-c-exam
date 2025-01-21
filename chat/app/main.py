# app/main.py
import logging
from fastapi import FastAPI, Request
from app.config import settings
from app.middlewares.correlation_id import CorrelationIdMiddleware

from chat.app.middlewares.request_metrics import RequestMetricsMiddleware

# Создаём объект логгера (при необходимости - отдельный логгер для каждого модуля)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def create_app() -> FastAPI:
    """
    Фабрика приложения FastAPI, позволяющая гибко управлять запуском.
    """
    fastapi_app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG
    )

    # Подключаем middleware для Correlation ID
    fastapi_app.add_middleware(CorrelationIdMiddleware)
    fastapi_app.add_middleware(RequestMetricsMiddleware)


    # Регистрируем тестовый эндпоинт
    @fastapi_app.get("/ping")
    async def ping(request: Request):
        # Пример лога с Correlation-ID
        correlation_id = request.state.correlation_id
        logger.info(f"[{correlation_id}] Обработка запроса /ping")
        return {"message": "pong"}

    return fastapi_app

app = create_app()
