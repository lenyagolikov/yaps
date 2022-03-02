from abc import ABC

from elasticsearch import AsyncElasticsearch


class BaseModelSearchManager(ABC):
    engine: AsyncElasticsearch
    index: str

    def __init__(self, index_name: str, engine: AsyncElasticsearch):
        self.engine = engine
        self.index = index_name
