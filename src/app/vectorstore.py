from elasticsearch import Elasticsearch, NotFoundError, RequestError
from typing import Any, Dict
import logging

from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings

from app.settings import es_connection_details

logger = logging.getLogger(__name__)

vectorstore = ElasticsearchStore(
    **es_connection_details,
    embedding=OpenAIEmbeddings(),
)


class BaseElasticSearch:
    client = Elasticsearch(es_connection_details["es_url"])
    index_name = es_connection_details["index_name"]

    def __init__(self): ...

    @property
    def body(self) -> Dict[str, Any]:
        body = {
            "mappings": {
                "properties": {
                    "metadata": {
                        "properties": {
                            "page": {"type": "long"},
                            "source": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                        }
                    },
                    "text": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "vector": {
                        "type": "dense_vector",
                        "dims": 1536,
                        "index": True,
                        "similarity": "cosine",
                    },
                }
            }
        }
        return body

    def create_index(self) -> None:
        try:
            if not self.client.indices.exists(index=self.index_name):
                self.client.indices.create(index=self.index_name, body=self.body)
                logger.info(f"Index '{self.index_name}' created with body: {self.body}")
            else:
                logger.info(f"Index '{self.index_name}' already exists.")
        except RequestError as e:
            logger.error(f"Error creating index '{self.index_name}': {e}")

    def delete_index(self) -> None:
        try:
            if self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)
                logger.info(f"Index '{self.index_name}' deleted.")
            else:
                logger.info(f"Index '{self.index_name}' does not exist.")
        except RequestError as e:
            logger.error(f"Error deleting index '{self.index_name}': {e}")

    @classmethod
    def delete_documents_by_source(cls, source: str):
        response = cls.client.delete_by_query(
            index=cls.index_name, body={"query": {"match": {"metadata.source": source}}}
        )
        return response
