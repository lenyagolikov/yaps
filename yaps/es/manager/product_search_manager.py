from typing import Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q

from yaps.es.manager.base_search_manager import BaseModelSearchManager
from yaps.es.schema import Product


class ProductSearchManager(BaseModelSearchManager):
    def __init__(self, engine: AsyncElasticsearch):
        super().__init__(Product.Index.name, engine)

    async def search(
        self,
        search_string: str,
        from_: Optional[int] = 0,
        limit: Optional[int] = 20,
    ) -> dict:
        query = {
            "query": Q(
                "match", text={"query": search_string, "operator": "and"}
            ).to_dict()
        }
        response = await self.engine.search(
            size=limit, index=self.index, body=query, from_=from_
        )

        result = {}
        for hit in response["hits"]["hits"]:
            result.update({int(hit["_id"]): hit["_source"]})

        return result

    async def get_info(self, id_: int) -> dict:
        query = {"query": Q("match", _id=id_).to_dict()}
        response = await self.engine.search(index=self.index, body=query)

        result = {}
        for hit in response["hits"]["hits"]:
            result.update({"id": int(hit["_id"]), **hit["_source"]})

        return result
