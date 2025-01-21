# app/metrics/prom_metrics.py
from prometheus_client import Counter, Histogram

# Общий счётчик запросов (пример с лейблами: метод, эндпоинт, статус-код)
REQUEST_COUNTER = Counter(
    name="fastapi_requests_total",
    documentation="Total count of requests to FastAPI endpoints",
    labelnames=["method", "endpoint", "http_status"]
)

# Гистограмма времени обработки запроса
REQUEST_LATENCY = Histogram(
    name="fastapi_request_latency_seconds",
    documentation="Histogram of request processing latency (seconds)",
    labelnames=["endpoint"]
)
