import os
from http import HTTPStatus

import pytest

from yaps.apps.api.schemas.users import AuthSchema


async def test_auth_by_token_success(client, auth_by_token_path):
    fields = {"access_token": os.getenv("ACCESS_TOKEN")}
    response = await client.post(auth_by_token_path, json=fields)
    body = await response.json()
    errors = AuthSchema().validate(body)
    assert response.status == HTTPStatus.OK
    assert errors == {}


async def test_auth_by_token_invalid_token(client, auth_by_token_path):
    fields = {"access_token": "badtoken"}
    response = await client.post(auth_by_token_path, json=fields)
    assert response.status == HTTPStatus.UNAUTHORIZED
