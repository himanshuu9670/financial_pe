from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pdf_editor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=900,
    task_soft_time_limit=840,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=30,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    result_expires=86400,
    worker_disable_rate_limits=True,
    task_routes={
        "app.workers.tasks.process_statement_pdf": {"queue": "ocr"},
        "app.workers.tasks.run_ocr_pipeline": {"queue": "ocr"},
        "app.workers.tasks.run_pdf_export": {"queue": "export"},
        "app.workers.tasks.run_ai_intelligence": {"queue": "ai"},
        "app.workers.tasks.cleanup_storage": {"queue": "default"},
    },
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "ocr": {"exchange": "ocr", "routing_key": "ocr"},
        "export": {"exchange": "export", "routing_key": "export"},
        "ai": {"exchange": "ai", "routing_key": "ai"},
    },
)
