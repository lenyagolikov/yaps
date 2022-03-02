from marshmallow import Schema
from marshmallow.fields import Int, Nested, Str, Float, List, Bool, Dict
from marshmallow.validate import Range


class ProductSchema(Schema):
    from_ = Int(
        data_key="from", load_default=None, description="Курсор для выдачи значений"
    )
    limit = Int(load_default=20, description="Количество возвращаемых значений")
    query = Str(data_key="q", required=True, description="Поисковый запрос")


class ProductResponseSchema(Schema):
    id = Int(required=True)
    name = Str(required=True)
    description = Str(required=True)
    text = Str(required=True)
    image = Str(required=True)
    min_price = Float(required=True)
    count_offers = Int(required=True)
    has_personal_offer = Bool(required=True)


class ProductListResponseSchema(Schema):
    products = Nested(ProductResponseSchema, many=True)


class ProductIdSchema(Schema):
    prod_id = Int(
        required=True, validate=Range(min=1, max=2147483647), description="ID товара"
    )


class OfferResponseSchema(Schema):
    cashback_percent = Float(missing=None)
    cashback_amount = Float(missing=None)
    old_price = Float(missing=None)
    partner_name = Str(required=True)
    partner_link = Str(required=True)
    currency = Str(required=True)
    curr_price = Float(required=True)
    cashback_type = Str(required=True)
    price_type = Str(required=True)


class ProductOfferResponseSchema(Schema):
    images = List(Str(), required=True)
    min_price = Float(required=True)
    offers = Nested(OfferResponseSchema, many=True)
    product_title = Str(required=True)
    product_description = Str(required=True)
    props = Dict(required=True)
