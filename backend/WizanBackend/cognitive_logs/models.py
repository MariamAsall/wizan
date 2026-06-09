# import uuid

# from django.db import models
# from django.conf import settings


# class CognitiveLog(models.Model):

#     id = models.UUIDField( primary_key=True, default=uuid.uuid4,  editable=False)
    
#     user= models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="cognitive_logs"
#     )

#     score= models.IntegerField()

#     quiz_answers= models.JSONField()

#     log_date= models.DateField()

#     created_at= models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.email} - {self.score}"



# Create your models here.


from django.db import models
from django.conf import settings
import uuid

class CognitiveLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cognitive_logs"
    )
    score = models.IntegerField(null=True, blank=True)        # ← add null=True (needed for skip quiz case)
    quiz_answers = models.JSONField(default=list)             # ← add default=list (needed for skip quiz)
    log_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    # ──  two new fields ──────────────────────
    final_score = models.IntegerField(null=True, blank=True)
    calculation_note = models.CharField(max_length=100, blank=True)
    # ─────────────────────────────────────────────

    def __str__(self):
        return f"{self.user.email} - {self.score}"