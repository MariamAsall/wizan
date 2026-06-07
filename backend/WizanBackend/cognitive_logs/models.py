from django.db import models
from django.conf import settings


class CognitiveLog(models.Model):
    user= models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cognitive_logs"
    )

    score= models.IntegerField()

    quiz_answers= models.JSONField()

    log_date= models.DateField()

    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.score}"



