import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


CORRELATION_ID_HEADER = "X-Correlation-Id"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware для сохранения или генерации Correlation-ID.
    Корреляционный ID выводится в логи и используется для трекинга запросов.
    """

    async def dispatch(self, request: Request, call_next):
        # Проверяем, есть ли уже Correlation-ID в заголовках
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)

        if not correlation_id:
            # Генерируем новый Correlation-ID, если он отсутствует
            correlation_id = str(uuid.uuid4())

        # Сохраняем Correlation-ID в объект запроса (можно использовать в логгере, эндпоинтах и т.д.)
        request.state.correlation_id = correlation_id

        # Пробрасываем Correlation-ID в ответ, чтобы потребитель API тоже видел идентификатор
        response: Response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response
