import time

from sqlalchemy.ext.asyncio import AsyncEngine

from yaps.db.manager.offer_manager import OfferManager
from yaps.db.manager.product_manager import ProductManager
from yaps.utils.db import is_available_postgres


class DBManager:
    engine: AsyncEngine

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    @property
    def products(self) -> ProductManager:
        return ProductManager(engine=self.engine)

    @property
    def offers(self) -> OfferManager:
        return OfferManager(engine=self.engine)

    async def check_conn_with_retries(
        self, retries: int = 5, timeout: float = 1
    ) -> bool:
        while not await is_available_postgres(self.engine) and retries > 1:
            retries -= 1
            time.sleep(timeout)
        return await is_available_postgres(self.engine)
