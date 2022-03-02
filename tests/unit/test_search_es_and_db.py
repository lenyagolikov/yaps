import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from yaps.db.manager.product_manager import ProductManager
from yaps.es.manager.product_search_manager import ProductSearchManager
from yaps.utils.db import connect_elasticsearch
from yaps.settings import Config


@pytest.mark.parametrize(
    "search_string",
    [
        "крем для рук",
        "глина",
        "маска"
    ],
)
async def test_es_success(search_string):
    engine = connect_elasticsearch()
    psm = ProductSearchManager(engine)
    products = await psm.search(search_string)
    await engine.close()
    assert isinstance(products, dict)

    engine = create_async_engine(
        f"postgresql+asyncpg://{Config.DB.test_url}",
        pool_size=Config.DB.pool_size,
        echo=Config.Logging.DB.echo,
        echo_pool=Config.Logging.DB.echo_pool,
        hide_parameters=False,
    )
    pm = ProductManager(engine)
    result = await pm.search(products=products)
    await engine.dispose()
    assert isinstance(result, list)
