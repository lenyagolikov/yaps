from http import HTTPStatus

from aiohttp import web, web_exceptions
from aiohttp_apispec import docs, response_schema, querystring_schema, match_info_schema

from yaps.apps.base_handler import BaseHandler, json_response
from yaps.settings import Config
from yaps.apps.api.schemas.products import (
    ProductSchema,
    ProductIdSchema,
    ProductListResponseSchema,
    ProductResponseSchema,
    ProductOfferResponseSchema,
)
from yaps.apps.api.schemas.responses import (
    BadRequestSchema,
    NotFoundSchema,
)


def format_image_link(image_link: str) -> str:
    if image_link:
        prefix = (
            Config.media_root if not image_link.startswith(Config.media_root) else ""
        )
        return (
            prefix
            + image_link
            + ".500x500."
            + ("png" if image_link.endswith(".png") else "jpg")
        )
    return ""


class PingDB(BaseHandler):
    async def get(self) -> web.Response:
        """
        /ping_db

        Проверяет коннект к БД
        Возвращает 200 код в случае успеха
        """
        return json_response(text="ok", status=HTTPStatus.OK)


class Ping(BaseHandler):
    async def get(self) -> web.Response:
        """
        /ping

        Проверяет, что приложение поднялось
        Возвращает 200 код в случае успеха
        """
        return json_response(text="ok", status=HTTPStatus.OK)


class ProductSearch(BaseHandler):
    @docs(tags=["product"], description="Поиск товаров")
    @querystring_schema(ProductSchema)
    @response_schema(
        ProductListResponseSchema,
        HTTPStatus.OK.value,
        description="Возвращает список товаров",
    )
    @response_schema(
        BadRequestSchema, HTTPStatus.BAD_REQUEST.value, description="Неверные параметры"
    )
    async def get(self) -> web.Response:
        query_params = self.request["querystring"]

        query = query_params["query"]
        from_ = query_params["from_"]
        limit = query_params["limit"]

        products = await self.es.products.search(
            search_string=query, limit=limit, from_=from_
        )

        user_email = self.user.email if self.user else None
        products = await self.db.products.search(
            products=products, user_email=user_email
        )

        products = ProductResponseSchema().dump(products, many=True)
        for product in products:
            product["image"] = format_image_link(image_link=product["image"])
        return json_response(data={"products": products}, status=HTTPStatus.OK)


class ProductOffers(BaseHandler):
    @docs(tags=["product"], description="Получение информации о товаре")
    @match_info_schema(ProductIdSchema)
    @response_schema(
        ProductOfferResponseSchema,
        HTTPStatus.OK.value,
        description="Возвращает информацию о товаре",
    )
    @response_schema(
        NotFoundSchema, HTTPStatus.NOT_FOUND.value, description="Товар не найден"
    )
    async def get(self, prod_id: int) -> web.Response:
        user_email = self.user.email if self.user else None
        product = await self.es.products.get_info(prod_id)

        if product:
            product_info = await self.db.offers.get_product_info(
                product=product, user_email=user_email
            )

            product = ProductOfferResponseSchema().dump(product_info)

        if not product:
            raise web_exceptions.HTTPNotFound(reason="not-found")

        for i in range(len(product["images"])):
            product["images"][i] = format_image_link(image_link=product["images"][i])
        return json_response(product, status=HTTPStatus.OK)


__all__ = ("PingDB", "Ping", "ProductSearch", "ProductOffers")
