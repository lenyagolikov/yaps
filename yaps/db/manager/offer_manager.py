from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from yaps.db.manager.base_manager import BaseModelManager
from yaps.db.schema import offers_table


class OfferManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        self.get_product_info_query = text(
            """SELECT
                min(coalesce(po2.price, o.price)) AS min_price,
                array_agg(p2.name) AS partner_names,
                array_agg(p2.link) AS partner_links,
                array_agg(coalesce(po2.price, o.price)) AS prices,
                array_agg(
                    CASE WHEN o.old_price IS NOT NULL
                        THEN o.old_price
                    WHEN po2.price IS NOT NULL
                        THEN o.price
                    ELSE o.old_price END
                ) AS old_prices,
                array_agg(CASE WHEN po2.price ISNULL THEN 'general' ELSE 'personal' END)
                    AS price_types,
                array_agg(coalesce(po2.cashback_percent, o.cashback_percent))
                    AS cashback_percents,
                array_agg(coalesce(po2.cashback_amount, o.cashback_amount))
                    AS cashback_amounts,
                array_agg(CASE WHEN po2.cashback_percent ISNULL THEN 'general' ELSE 'personal' END)
                    AS cashback_types
            FROM offers o
            JOIN partners p2 ON o.partner_id = p2.id
            LEFT JOIN personal_offers po2 on (o.id = po2.offer_id AND po2.user_email = :user_email)
            WHERE o.product_id = :prod_id
            GROUP BY o.product_id;
        """
        )
        super().__init__(offers_table, engine)

    async def get_product_info(self, product: dict, user_email: Optional[str]) -> dict:
        async with self.engine.connect() as conn:
            cur = await conn.execute(
                self.get_product_info_query,
                {"prod_id": product["id"], "user_email": user_email},
            )

        aggregated_data = cur.fetchone()
        return (
            self.__transform_product_info(product, aggregated_data)
            if aggregated_data
            else {}
        )

    @staticmethod
    def __transform_product_info(product: dict, aggregated_data: Any) -> dict:
        offers = []
        for i, partner_name in enumerate(aggregated_data.partner_names):
            curr_price = aggregated_data.prices[i]
            old_price = aggregated_data.old_prices[i]
            curr_cashback_percent = aggregated_data.cashback_percents[i]
            curr_cashback_amount = aggregated_data.cashback_amounts[i]
            partner_link = aggregated_data.partner_links[i]
            price_type = aggregated_data.price_types[i]
            cashback_type = aggregated_data.cashback_types[i]

            offers.append(
                {
                    "partner_name": partner_name,
                    "partner_link": partner_link,
                    "curr_price": curr_price,
                    "old_price": old_price,
                    "cashback_percent": curr_cashback_percent,
                    "cashback_amount": curr_cashback_amount,
                    "price_type": price_type,
                    "cashback_type": cashback_type,
                    "currency": "RUB",
                }
            )
        product["offers"] = offers
        product["product_description"] = product["text"]
        product["product_title"] = product["name"]
        product["min_price"] = aggregated_data.min_price

        return product
