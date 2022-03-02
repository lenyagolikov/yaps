from http import HTTPStatus

import pytest


@pytest.fixture
def ping_path() -> str:
    return "/api/v1/ping"


@pytest.fixture
def ping_db_path() -> str:
    return "/api/v1/ping_db"


async def test_ping(client, ping_path):
    response = await client.get(ping_path)
    assert response.status == HTTPStatus.OK


async def test_ping_db(client, ping_db_path):
    response = await client.get(ping_db_path)
    assert response.status == HTTPStatus.OK
