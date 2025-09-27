import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insighthub.settings")

## Get the base REDIS URL, default to redis' default
BASE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

app = Celery("insighthub")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.broker_url = BASE_REDIS_URL

app.conf.beat_schedule = {
    "add-every-180-seconds": {
        "task": "insighthub.tasks.process_failed_payloads",
        "schedule": 180.0,
    },
}
