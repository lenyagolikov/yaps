import time

from elasticsearch import AsyncElasticsearch

from yaps.es.manager.product_search_manager import ProductSearchManager
from yaps.utils.db import is_available_es


class ElasticSearchManager:
    engine: AsyncElasticsearch

    def __init__(self, engine: AsyncElasticsearch):
        self.engine = engine

    @property
    def products(self) -> ProductSearchManager:
        return ProductSearchManager(engine=self.engine)

    async def check_conn_with_retries(
        self, retries: int = 5, timeout: float = 1
    ) -> bool:
        while not await is_available_es(self.engine) and retries > 1:
            retries -= 1
            time.sleep(timeout)
        return await is_available_es(self.engine)
