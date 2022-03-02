import logging
import sqlalchemy
import asyncpg

from sqlalchemy.ext.asyncio import AsyncEngine
from elasticsearch import AsyncElasticsearch
from yaps.settings import Config


async def is_available_db(engine: AsyncEngine, es: AsyncElasticsearch) -> bool:
    return await is_available_es(es) and await is_available_postgres(engine)


async def is_available_es(es: AsyncElasticsearch) -> bool:
    try:
        return await es.ping()
    except Exception as e:
        logging.exception(
            "When checking availability of a database in 'is_available_es' function"
            " an exception was occurred: %s",
            str(e),
        )
        return False


async def is_available_postgres(engine: AsyncEngine) -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))

        return True
    except (
        sqlalchemy.exc.OperationalError,
        ConnectionRefusedError,
        asyncpg.exceptions.InvalidPasswordError,
    ):
        return False
    except Exception as e:
        logging.exception(
            "When checking availability of a database in 'is_available_postgres' function"
            " an exception was occurred: %s",
            str(e),
        )
        return False


def connect_elasticsearch() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=Config.Elastic.hosts)
