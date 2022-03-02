"""
Service settings
"""
import logging
import pathlib
from os import getenv

import yarl

from aiohttp_cache import RedisConfig
from pydantic.datetime_parse import timedelta


class Config:
    base_path = pathlib.Path(__file__).parent

    debug = getenv("DEBUG")

    app_version = getenv("APP_VERSION", "0.0.1")

    # Настройки для gunicorn
    host = getenv("HOST", "0.0.0.0")
    port = getenv("PORT", "8080")
    workers_num = int(getenv("WORKERS_NUM", 4))

    # Тут идея с эппами как в Джанго
    # В настройках описываем все доступные приложения, а в apps записываем только "включенные"

    # All apps
    api_app = "api"
    auth_app = "auth"

    # Enabled apps
    apps = [api_app, auth_app]

    # The root path for media
    media_root = "/media/"

    elastic_enabled = False

    class Elastic:
        hosts = getenv("ES_HOSTS", "0.0.0.0:9200").split(",")
        shards_num = int(getenv("ES_SHARDS_NUM", "2"))
        replicas_num = int(getenv("ES_REPLICAS_NUM", "2"))

    class DB:
        config = {
            # asyncpg не может в dsn с несколькими хостами, поэтому костылим
            # https://github.com/MagicStack/asyncpg/issues/352
            "hosts": getenv("POSTGRES_HOSTS", "localhost:5432").split(",")[0],
            "password": getenv("POSTGRES_PWD", "password"),
            "user": getenv("POSTGRES_USER", "root"),
            "database": getenv("POSTGRES_DB", "yaps"),
        }

        test_config = {
            "hosts": getenv("TEST_POSTGRES_HOSTS", "localhost:5432").split(",")[0],
            "password": getenv("TEST_POSTGRES_PASSWORD", "password"),
            "user": getenv("TEST_POSTGRES_USER", "root"),
            "database": getenv("TEST_POSTGRES_DB", "test"),
        }

        url = "{user}:{password}@{hosts}/{database}".format(**config)
        test_url = "{user}:{password}@{hosts}/{database}".format(**test_config)

        pool_size = int(getenv("POOL_SIZE", 10))
        consumer_pool_size = int(getenv("CONSUMER_POOL_SIZE", 4))

        elasticsearch_hosts = getenv("ES_HOSTS", "").split(";")

    class Cache:
        class CacheType:
            memory = "memory"
            redis = "redis"
            all_types = {_: _ for _ in [memory, redis]}

        class RedisConfig:
            url = yarl.URL(getenv("REDIS_URL", "redis://localhost:6379/0"))
            config = RedisConfig(db=int(url.path[1:]), host=url.host, port=url.port)

        cache_type = CacheType.all_types.get(getenv("CACHE_TYPE"), CacheType.memory)
        backend_config = None if cache_type is CacheType.memory else RedisConfig.config

    class YandexOAuth:
        auth_url = "https://oauth.yandex.ru/authorize"
        login_url = "https://login.yandex.ru/info"
        app_id = getenv("YANDEX_PASSPORT_APP_ID")

    class Auth:
        auth_header = "Authorization"
        token_type = "Bearer"
        token_len = 64  # len(len(hashlib.sha256(<bin>).hexdigest())
        token_lifetime = timedelta(hours=1)

    class Logging:
        level = logging.INFO
        format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"

        class DB:
            echo = bool(getenv("ECHO_DB"))
            echo_pool = bool(getenv("ECHO_POOL"))

    class AlertBot:
        token = getenv("ALERT_BOT_TOKEN")
        chat_id = int(getenv("ALERT_CHAT_ID"))

    class General:
        prod = False if getenv("PROD") is None else True

    nginx_logs_path = pathlib.Path("/var/log/nginx/access.log")
