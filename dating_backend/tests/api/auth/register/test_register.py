from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.conf import URLS

BASE_DIR = Path(__file__).parent
FIXTURES_PATH = BASE_DIR / "fixtures"


@pytest.mark.parametrize(
    ("id_", "expected_status", "fixtures"),
    [
        (
            2323,
            status.HTTP_409_CONFLICT,
            [
                FIXTURES_PATH / "meet.user.json",
            ],
        ),
        (
            121,
            status.HTTP_201_CREATED,
            [
                FIXTURES_PATH / "meet.user.json",
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures("_common_api_fixture")
async def test_register(
    client: AsyncClient,
    id_: int,
    expected_status: int,
    db_session: None,
) -> None:
    response = await client.post(
        URLS["auth"]["register"], json={"id": id_}
    )
    assert response.status_code == expected_status
