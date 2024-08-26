from celery import Celery

from app import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_routes={
        "app.tasks.knowledge_document.*": {"queue": "document_queue"},
    },
)

celery_app.autodiscover_tasks(["app.tasks.knowledge_document"])
