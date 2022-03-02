from aiohttp import web
from .handlers import Ping, PingDB, ProductSearch, ProductOffers


def register_api_routes(app: web.Application, prefix: str = ""):
    app.router.add_view(prefix + r"/ping_db", PingDB)
    app.router.add_view(prefix + r"/ping", Ping)
    app.router.add_view(prefix + r"/product/search", ProductSearch)
    app.router.add_view(prefix + r"/product/{prod_id:\d+}", ProductOffers)
