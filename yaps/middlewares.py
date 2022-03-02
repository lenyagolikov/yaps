import sys
from http import HTTPStatus
from typing import List, Callable

from aiohttp import web, web_exceptions
from aiohttp_apispec import validation_middleware

from yaps.apps.base_handler import error_response, ErrMsg
from yaps.apps.auth.middlewares import auth_middleware
from yaps.utils.db import is_available_es, is_available_postgres

from yaps.utils import logging as log
from yaps.utils.event.type import EventType

stderr_handler = log.get_stream_handler(sys.stderr)
logger = log.get_logger(__name__, handlers=[stderr_handler])


def get_middlewares() -> List[Callable]:
    """
    Тут регистрируем все миддлваеры
    :return: список миддлваеров
    """
    return [
        exception_middleware,
        availability_db,
        validation_middleware,
        auth_middleware,
    ]


@web.middleware
async def availability_db(request: web.Request, handler: Callable) -> web.Response:
    if not await is_available_postgres(request.app["db_engine"]):
        await request.app['event_engine'].push(EventType.PGDown, request.app)
        raise web_exceptions.HTTPServiceUnavailable(reason=ErrMsg.PG_UNAVAILABLE)

    await request.app['event_engine'].push(EventType.PGAlive, request.app)

    if not await is_available_es(
        request.app["search_engine"]
    ):
        await request.app['event_engine'].push(EventType.ESDown, request.app)
        raise web_exceptions.HTTPServiceUnavailable(reason=ErrMsg.ES_UNAVAILABLE)

    await request.app['event_engine'].push(EventType.ESAlive, request.app)

    return await handler(request)


@web.middleware
async def exception_middleware(request: web.Request, handler: Callable) -> web.Response:
    try:
        response = await handler(request)

    except web_exceptions.HTTPUnprocessableEntity:
        err_msg = ErrMsg.BAD_PARAMETERS
        response = error_response(
            message=err_msg,
            status=HTTPStatus.BAD_REQUEST,
        )

    except web.HTTPError as e:
        # TODO: тут возможно надо добавить получение описания ошибки из ErrMsg класса
        #  но тогда в нём надо получать атрибуты класса и по названиям ошибки получать ключи. Доделаю @lpshkn
        err_msg = e.reason
        logger.error(err_msg)
        response = error_response(
            message=err_msg,
            status=e.status,
        )

    except Exception as e:
        err_msg = str(e)
        await request.app['event_engine'].push(EventType.UnhandledException, request.app, f'{err_msg}')
        response = error_response()

    finally:
        if response.status < 400:
            logger.info(
                "%s %s %s %s",
                request.method,
                request.path,
                response.status,
                request.remote,
            )
        else:
            logger.error(
                "%s %s %s %s %s",
                request.method,
                request.path,
                response.status,
                request.remote,
                err_msg,
            )

    return response
