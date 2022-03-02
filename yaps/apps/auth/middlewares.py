from typing import Callable

from aiohttp import web
from aiohttp_cache.backends import BaseCache

from yaps.utils.auth.auth_token import AuthUtils
from yaps.utils.auth.auth_user import AuthUser


@web.middleware
async def auth_middleware(request: web.Request, handler: Callable) -> web.Response:
    """
    Get auth_token from Config.Auth.auth_header and validate it
    User info could be get by his auth token in cache. Info format:
    {
        'email': <str>,
        'access_token': <str>  # yandex access token
    }
    """
    cache: BaseCache = request.app["cache"]

    token = AuthUtils.extract_auth_token(request)
    if token:
        user = await cache.get(token)
        if user:
            request["user"] = AuthUser(
                email=user["email"], access_token=user["access_token"]
            )

    return await handler(request)
