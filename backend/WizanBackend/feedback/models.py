from django.db import models
from django.conf import settings


class ChatFeedback(models.Model):

    RATING_CHOICES = [
        (1, "Like"),
        (-1, "Dislike"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_feedbacks"
    )

    question = models.TextField()

    answer = models.TextField()

    rating = models.IntegerField(
        choices=RATING_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.rating}"