# app/middlewares/request_metrics.py
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.metrics.prom_metrics import REQUEST_COUNTER, REQUEST_LATENCY

logger = logging.getLogger(__name__)

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware, которая:
      1) Считает количество запросов по методам, эндпоинтам и статус-кодам.
      2) Измеряет время обработки (latency) каждого запроса.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response: Response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Определяем лейблы
        method = request.method
        endpoint = request.url.path
        http_status = response.status_code

        # Увеличиваем счетчик запросов
        REQUEST_COUNTER.labels(method=method, endpoint=endpoint, http_status=http_status).inc()

        # Записываем время обработки в гистограмму
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(process_time)

        return response
