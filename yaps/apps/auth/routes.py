from aiohttp import web
from .handlers import GetAuthUrl
from .handlers import ParseAccessToken
from .handlers import AuthByAccessToken
from .handlers import AuthButton
from .handlers import GetUserEmail


def register_auth_routes(app: web.Application, prefix: str = ""):
    app.router.add_view(prefix + r"/", AuthButton)
    app.router.add_view(prefix + r"/get_url", GetAuthUrl)
    app.router.add_view(prefix + r"/parse_token", ParseAccessToken)
    app.router.add_view(prefix + r"/by_token", AuthByAccessToken)
    app.router.add_view(prefix + r"/get_user_email", GetUserEmail)
