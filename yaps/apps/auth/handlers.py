import json
from datetime import datetime
from http import HTTPStatus

import requests
from aiohttp import web, web_exceptions
from aiohttp_apispec import docs, response_schema, request_schema

from yaps.apps.api.schemas.responses import UnauthorizedSchema
from yaps.apps.api.schemas.users import TokenSchema, AuthSchema
from yaps.apps.base_handler import BaseHandler, json_response, ErrMsg
from yaps.settings import Config
from yaps.utils.auth.auth_token import AuthUtils
from yaps.utils.auth.yandex_oauth import YandexOAuthUtil


class AuthButton(BaseHandler):
    async def get(self) -> web.Response:
        body = """<html><head></head><body>
        <script>
            fetch('/api/v1/auth/get_url').then(response=>response.json()).then(function (data) {
                document.getElementsByTagName('body')[0].innerHTML = '<a href="'+data+'">Авторизоваться</a>'
            })
        </script>
        </body></html>"""
        return web.Response(text=body, status=HTTPStatus.OK, content_type="text/html")


class ParseAccessToken(BaseHandler):
    async def get(self) -> web.Response:
        body = """<script>document.location.hash.slice(1).split('&').forEach(function (param) {
            const paramParts = param.split('=');
            const key = paramParts[0];
            const value = paramParts[1];
            if (key === 'access_token') {
                try {
                    fetch('/api/v1/auth/by_token', {method: 'POST', body:JSON.stringify({access_token: value})})
                } catch (e) {

                }
                document.location = '/';
            }
        });</script>"""
        return web.Response(body=body, status=HTTPStatus.OK, content_type="text/html")


class GetAuthUrl(BaseHandler):
    yandex_oauth: YandexOAuthUtil = YandexOAuthUtil()

    async def get(self) -> web.Response:
        auth_url = self.yandex_oauth.get_auth_url()
        if not auth_url:
            raise web_exceptions.HTTPInternalServerError(
                reason="YANDEX_APP_ID is not set"
            )

        return json_response(auth_url, status=HTTPStatus.OK)


class AuthByAccessToken(BaseHandler):
    yandex_oauth: YandexOAuthUtil = YandexOAuthUtil()
    auth_utils: AuthUtils = AuthUtils()

    @docs(tags=["auth"], description="Авторизация по токену")
    @request_schema(TokenSchema)
    @response_schema(
        AuthSchema, HTTPStatus.OK.value, description="Возвращает данные клиента"
    )
    @response_schema(
        UnauthorizedSchema,
        HTTPStatus.UNAUTHORIZED.value,
        description="Авторизация не пройдена",
    )
    async def post(self) -> web.Response:
        access_token = await self.get_from_request("access_token")

        ya_answer = requests.get(self.yandex_oauth.get_login_url(access_token))

        try:
            ya_credentials = json.loads(ya_answer.content)
        except json.JSONDecodeError as e:
            raise web_exceptions.HTTPUnauthorized(reason=ErrMsg.BAD_TOKEN) from e

        email = ya_credentials["default_email"]

        auth_token = self.auth_utils.gen_auth_token(
            user_email=ya_credentials["default_email"], access_token=access_token
        )

        user = {"email": email, "access_token": access_token}
        await self.cache.set(
            key=auth_token, value=user, expires=Config.Auth.token_lifetime.seconds
        )

        auth_data = AuthSchema().dump(
            {
                "auth_token": auth_token,
                "email": email,
                "expires_at": (datetime.now() + Config.Auth.token_lifetime).timestamp(),
            }
        )
        return json_response(auth_data, status=HTTPStatus.OK)


class GetUserEmail(BaseHandler):
    async def get(self) -> web.Response:
        email = self.user.email if self.user else None

        return json_response(email, status=HTTPStatus.OK)


__all__ = (
    "GetUserEmail",
    "AuthButton",
    "GetAuthUrl",
    "ParseAccessToken",
    "AuthByAccessToken",
)
