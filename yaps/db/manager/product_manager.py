from typing import Optional, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from yaps.db.schema import products_table
from yaps.db.manager.base_manager import BaseModelManager


class ProductManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        super().__init__(products_table, engine)

    async def search(
        self,
        products: dict,
        user_email: Optional[str] = None,
    ) -> List[dict]:
        async with self.engine.connect() as conn:
            sql = """
            SELECT offers.product_id,
                   min(CASE WHEN po.price ISNULL THEN offers.price ELSE po.price END) min_price,
                   bool_or(po.price IS NOT NULL) AS has_personal_offer,
                   count(offers) count_offers
            FROM offers LEFT JOIN personal_offers po ON offers.id = po.offer_id AND po.user_email = :user_email
            WHERE offers.product_id = ANY(:products_ids)
            GROUP BY offers.product_id;
            """
            result = await conn.execute(
                text(sql),
                {
                    "products_ids": (products.keys()),
                    "user_email": user_email,
                },
            )

            result_products = []
            for row in result:
                product = products.pop(row["product_id"])
                result_products.append(
                    {
                        "id": row["product_id"],
                        "min_price": row["min_price"],
                        "count_offers": row["count_offers"],
                        "has_personal_offer": row["has_personal_offer"],
                        "image": product["images"][0],
                        **product,
                    }
                )

            return result_products
