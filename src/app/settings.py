import os

PROJECT_NAME = os.getenv("PROJECT_NAME")

# elasticsearch
ES_URL = os.getenv("ES_URL")
ES_INDEX_NAME = os.getenv("ES_INDEX_NAME")
es_connection_details = {"es_url": ES_URL, "index_name": ES_INDEX_NAME}

# mongodb
DATABASE_URL = os.getenv("DATABASE_URL")


# celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
