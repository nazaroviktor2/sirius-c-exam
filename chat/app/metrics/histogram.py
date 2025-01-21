# app/metrics/histogram.py
import time
from typing import Any, Callable
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Глобальная структура для хранения "распределения" времени
# Здесь используем defaultdict(list) для упрощённой версии
db_latency_histogram = defaultdict(list)


def measure_db_latency_histogram(func: Callable) -> Callable:
    """
    Декоратор для замера времени выполнения (latency) вызова функции,
    например, интеграции с базой данных.

    В данном примере сохраняем результат в db_latency_histogram.
    В продакшене: можно записывать в базу данных или отправлять в систему мониторинга.
    """

    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time

        # Допустим, ключ = имя функции
        db_latency_histogram[func.__name__].append(elapsed)

        logger.info(f"[DB LATENCY] Function: {func.__name__} took {elapsed:.4f} seconds")
        return result

    return wrapper
