import logging
from functools import partial

from aiomisc.log import basic_config
from aiohttp import web
from aiohttp_cache import setup_cache
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_swagger import setup_swagger
from sqlalchemy.ext.asyncio import create_async_engine

from yaps.routes import register_routes
from yaps.middlewares import get_middlewares
from yaps.settings import Config
from yaps.utils.alert_bot.bot import create_alert_bot
from yaps.utils.db import connect_elasticsearch
from yaps.utils.event.event import create_event_engine
from yaps.utils.event.type import EventType


async def init_db_engine(base_app: web.Application):
    base_app["db_engine"] = create_async_engine(
        f"postgresql+asyncpg://{Config.DB.url}",
        pool_size=Config.DB.pool_size,
        echo=Config.Logging.DB.echo,
        echo_pool=Config.Logging.DB.echo_pool,
        hide_parameters=False,
    )


async def init_search_engine(base_app: web.Application):
    base_app["search_engine"] = connect_elasticsearch()


async def close_db_engine(base_app: web.Application):
    """
    Close all active connections
    """
    await base_app["db_engine"].dispose()


async def close_search_engine(base_app: web.Application):
    await base_app["search_engine"].close()


def make_app() -> web.Application:
    basic_config(Config.Logging.level, buffered=False)
    base_app = web.Application(middlewares=get_middlewares())
    setup_aiohttp_apispec(base_app)
    async def swagger(app):
        setup_swagger(
            app=app, swagger_url='/api/doc', swagger_info=app['swagger_dict']
        )
    base_app.on_startup.append(swagger)

    setup_cache(
        base_app,
        cache_type=Config.Cache.cache_type,
        backend_config=Config.Cache.backend_config,
    )
    logging.info("setup cache: %s", Config.Cache.cache_type)

    register_routes(base_app)

    base_app.on_startup.append(init_db_engine)
    base_app.on_startup.append(init_search_engine)

    base_app.cleanup_ctx.append(create_event_engine)
    base_app.cleanup_ctx.append(partial(create_alert_bot, Config.AlertBot.token, Config.AlertBot.chat_id))

    base_app.on_cleanup.append(close_db_engine)
    base_app.on_cleanup.append(close_search_engine)


    return base_app


app = make_app()

if __name__ == "__main__":
    web.run_app(app, host=Config.host, port=Config.port)
