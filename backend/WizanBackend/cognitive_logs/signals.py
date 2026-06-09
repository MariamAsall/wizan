# # cognitive_logs/signals.py

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import CognitiveLog
# from ai.total_score import calculate_total_score


# @receiver(post_save, sender=CognitiveLog)
# def enrich_with_total_score(sender, instance, created, **kwargs):
#     if not created:
#         return
#     if instance.final_score is not None:
#         return

#     # quiz_score comes from his SubmitQuizAPIView
#     # if user skipped, score field will be None
#     result = calculate_total_score(
#         user=instance.user,
#         quiz_score=instance.score,
#     )

#     CognitiveLog.objects.filter(pk=instance.pk).update(
#         final_score=result["final_score"],
#         calculation_note=result["calculation_note"],
#     )


# backend/WizanBackend/cognitive_logs/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CognitiveLog


@receiver(post_save, sender=CognitiveLog)
def enrich_with_total_score(sender, instance, created, **kwargs):
    """
    Fires automatically after SubmitQuizAPIView saves CognitiveLog.
    Reads his quiz score → adds history + behavioral → saves final_score.
    No changes to his views.py needed.
    """
    if not created:
        return
    if instance.final_score is not None:
        return

    # import here to avoid circular imports
    from ai.total_score import calculate_total_score

    result = calculate_total_score(
        user=instance.user,
        quiz_score=instance.score,   # ← reads HIS calculated score
    )

    # use filter().update() — never instance.save() — avoids infinite loop
    CognitiveLog.objects.filter(pk=instance.pk).update(
        final_score=result["final_score"],
        calculation_note=result["calculation_note"],
    )