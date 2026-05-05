"""Celery application configuration.

Run a worker with:
    celery -A src.workers.celery_app worker --loglevel=info

Run the beat scheduler (for periodic tasks):
    celery -A src.workers.celery_app beat --loglevel=info
"""

from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "visual_search_engine",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,        # hard kill after 30 minutes
    task_soft_time_limit=25 * 60,   # raise SoftTimeLimitExceeded after 25
    worker_prefetch_multiplier=1,   # one task at a time per worker
    worker_max_tasks_per_child=100, # restart worker after 100 tasks to avoid memory leaks
)
