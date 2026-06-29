# backend/WizanBackend/cognitive_logs/apps.py

from django.apps import AppConfig


class CognitiveLogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cognitive_logs"

    def ready(self):
        import cognitive_logs.signals   # ← registers your signal on startup