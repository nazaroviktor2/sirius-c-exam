# tests/test_ping.py
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def test_client():
    """
    Фикстура для создания клиента,
    используется во всех тестах в рамках одной сессии.
    """
    with TestClient(app) as client:
        yield client


def test_ping_endpoint(test_client):
    """
    Проверяем, что эндпоинт /ping возвращает 200 и нужное тело ответа.
    """
    response = test_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
