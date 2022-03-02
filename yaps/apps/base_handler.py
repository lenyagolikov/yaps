import json
import inspect
import functools
from decimal import Decimal
from http import HTTPStatus
from json import JSONDecodeError
from typing import Optional, Union, Any, List, Callable
from uuid import UUID

import pydantic
from aiohttp import web, hdrs
from aiohttp.web_response import StreamResponse
from aiohttp_cache.backends import BaseCache

from yaps.db.db_manager import DBManager
from yaps.es.es_manager import ElasticSearchManager
from yaps.utils.auth.auth_user import AuthUser


def _uuid_json(obj):
    if isinstance(obj, UUID):
        return obj.hex
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Unable to serialize {!r}".format(obj))


def json_response(*args, **kwargs) -> web.Response:
    """
    Расширенный json_response с кастомным json дампером,
    умеющим сериализовывать UUID/Decimal
    """
    return web.json_response(
        *args, **kwargs, dumps=functools.partial(json.dumps, default=_uuid_json)
    )


def error_response(
    message: Optional[str] = None, status: int = HTTPStatus.INTERNAL_SERVER_ERROR
) -> web.Response:
    """
    Base error response
    """
    status = HTTPStatus(status)
    body = {"message": message or status.description}
    return web.json_response(body, status=status)


class ErrMsg:
    """
    Class with app error messages
    """

    BAD_PARAMETERS: str = "bad-parameters"
    BAD_TOKEN: str = "bad-token"
    NOT_FOUND: str = "not-found"
    METHOD_NOT_ALLOWED: str = "method-not-allowed"
    REQUEST_LIMIT_EXCEEDED: str = "request-limit-exceeded"
    PG_UNAVAILABLE: str = "postgres-unavailable"
    ES_UNAVAILABLE: str = "elasticsearch-unavailable"


class BaseHandler(web.View):
    """
    Базовый обработчик. Позволяет инлайнить path параметры в параметры обработчиков.
    Также предоставляет доступ к БД и кешу
    """

    @property
    def db(self) -> DBManager:
        return DBManager(engine=self.request.app["db_engine"])

    @property
    def es(self) -> ElasticSearchManager:
        return ElasticSearchManager(engine=self.request.app["search_engine"])

    @property
    def cache(self) -> BaseCache:
        return self.request.app["cache"]

    @property
    def user(self) -> Optional[AuthUser]:
        """
        Request user - None if user is not authorized
        AuthUser is set in yaps.apps.auth.middlewares.auth_middleware
        """
        return self.request.get("user")

    async def db_is_alive(self) -> bool:
        return await self.db.check_conn_with_retries(retries=2, timeout=0.5)

    async def get_from_request(self, obj: Union[str, type]) -> Any:
        """
        Позволяет получать десериализованный обьект из

        :param obj: ключ параметра или pydantic тип, который передается в теле запроса
        :return: параметр или pydantic обьект
        """
        try:
            req_data = await self.request.json()
            if isinstance(obj, str):
                return req_data.get(obj)
            return obj(**req_data)
        except (pydantic.error_wrappers.ValidationError, JSONDecodeError):
            return None

    def _get_typed_params(self, method: Callable) -> List[Any]:
        """
        Вносит в aiohttp немного FastAPI
        Инлайнит в параметры обработчика path параметры
        """
        path_params = []
        for param_name, param_type in inspect.getfullargspec(
            method
        ).annotations.items():
            if param_name == "return":
                continue
            param = self.request.match_info.get(param_name)
            path_params.append(param_type(param))
        return path_params

    async def _iter(self) -> StreamResponse:
        """
        Переопределяем базовый метод, чтобы инлайнить path параметры в парметры обработчиков
        """
        if self.request.method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request.method.lower(), None)
        if method is None:
            self._raise_allowed_methods()

        method_params = self._get_typed_params(method)
        resp = await method(*method_params)
        return resp


__all__ = ("error_response", "ErrMsg", "BaseHandler", "json_response")
