from http import HTTPStatus

import pytest

from yaps.apps.api.schemas.products import ProductListResponseSchema


@pytest.mark.parametrize(
    "params",
    [
        {"q": "крем для рук"},
        {"q": "глина"},
        {"q": "натуральное мыло ручной работы"},
    ],
)
async def test_product_search_success(client, search_product_path, params):
    response = await client.get(search_product_path, params=params)
    assert response.status == HTTPStatus.OK

    body = await response.json()
    errors = ProductListResponseSchema().validate(body)
    assert errors == {}


@pytest.mark.parametrize(
    "params",
    [
        {"q": "крем для рук", "limit": 2},
        {"q": "маска", "limit": 1}
    ],
)
async def test_product_search_success_with_limit(client, search_product_path, params):
    response = await client.get(search_product_path, params=params)
    assert response.status == HTTPStatus.OK
    
    body = await response.json()
    errors = ProductListResponseSchema().validate(body)
    assert errors == {}
    
    limit = params["limit"]
    assert len(body["products"]) == limit


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"query": "глина"},
        {"limit": 5, "from": 3},
    ],
)
async def test_product_search_bad_params(client, search_product_path, params):
    response = await client.get(search_product_path, params=params)
    assert response.status == HTTPStatus.BAD_REQUEST
