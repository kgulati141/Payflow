import os
from celery import Celery

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")

celery_app = Celery(
    "payflow",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/1",
    include=["app.tasks.payment_tasks"]
)

celery_app.conf.timezone = "Asia/Kolkata"
celery_app.conf.enable_utc = False