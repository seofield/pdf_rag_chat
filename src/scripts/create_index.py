import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch

from app import settings

es = Elasticsearch(hosts=settings.ES_URL)

mapping = {
    "mappings": {
        "properties": {
            "metadata": {
                "properties": {
                    "page": {"type": "long"},
                    "source": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
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

if not es.indices.exists(index=settings.ES_INDEX_NAME):
    es.indices.create(index=settings.ES_INDEX_NAME, body=mapping)
    print(f"Index '{settings.ES_INDEX_NAME}' has been created successfully.")
else:
    print(f"Index '{settings.ES_INDEX_NAME}' already exists.")
