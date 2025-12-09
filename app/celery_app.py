from celery import Celery

celery_app = Celery(
    "broadcast_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# ✅ THIS IS THE FIX
celery_app.autodiscover_tasks(["app.broadcast"])
