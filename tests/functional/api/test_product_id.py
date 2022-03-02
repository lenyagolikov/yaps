from http import HTTPStatus

import pytest

from yaps.apps.api.schemas.products import ProductOfferResponseSchema


@pytest.mark.parametrize(
    "prod_id",
    [
        7512,
        "7512",
    ],
)
async def test_product_id_success(client, product_offers_path, prod_id):
    response = await client.get(f"{product_offers_path}/{prod_id}")
    assert response.status == HTTPStatus.OK
    
    body = await response.json()
    errors = ProductOfferResponseSchema().validate(body)
    assert errors == {}



@pytest.mark.parametrize(
    "prod_id",
    [
        "hello",
        "-1"
        "50000"
    ],
)
async def test_product_id_not_found(client, product_offers_path, prod_id):
    response = await client.get(f"{product_offers_path}/{prod_id}")
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "prod_id",
    [
        "32141242412331231231231234",
        23213123123123123123123123123
    ],
)
async def test_product_id_bad_params(client, product_offers_path, prod_id):
    response = await client.get(f"{product_offers_path}/{prod_id}")
    assert response.status == HTTPStatus.BAD_REQUEST
