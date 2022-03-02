from typing import Any, Callable

import pytest

from yaps.app import make_app
from yaps.settings import Config


@pytest.fixture
async def client(aiohttp_client: Callable) -> Any:
    Config.DB.url = Config.DB.test_url
    app = make_app()

    return await aiohttp_client(app)


@pytest.fixture
def search_product_path() -> str:
    return "/api/v1/product/search"


@pytest.fixture
def product_offers_path() -> str:
    return "/api/v1/product"


@pytest.fixture
def auth_by_token_path() -> str:
    return "api/v1/auth/by_token"
