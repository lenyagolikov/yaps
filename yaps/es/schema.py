from elasticsearch_dsl import Document, Text, Object

from yaps.es.analizer import fts_analyzer
from yaps.settings import Config


class Product(Document):
    name = Text(required=True, analyzer=fts_analyzer, search_analyzer=fts_analyzer)
    description = Text(
        required=True, analyzer=fts_analyzer, search_analyzer=fts_analyzer
    )
    text = Text(required=True, analyzer=fts_analyzer, search_analyzer=fts_analyzer)
    images = Text(required=True)
    props = Object(required=True)

    class Index:
        name = "products"
        settings = {
            "number_of_shards": Config.Elastic.shards_num,
            "number_of_replicas": Config.Elastic.replicas_num,
        }


INDICES = [Product]
