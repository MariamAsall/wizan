import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "WizanBackend.settings"
)

broker = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
app = Celery('WizanBackend', broker=broker, backend=broker)

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-task-deadlines-every-hour": {
        "task": "notifications.tasks.check_deadlines",
        "schedule": 3600.0,
    },
}