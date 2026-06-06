from django.db import models

# Create your models here.
import uuid


QUESTIONS = [
    ("How focused did you feel today?", "scale_1_5", 3),
    ("Did you complete your highest-priority task?", "yes_no", 5),
    ("How overwhelmed did you feel today?", "scale_1_5", 5),
    ("Did you procrastinate on important work?", "yes_no", 4),
    ("How motivated did you feel today?", "scale_1_5", 5),
    ("Did you study today?", "yes_no", 3),
    ("How effectively did you manage your schedule?", "scale_1_5", 5),
    ("Did you miss any deadlines today?", "yes_no", 5),
]


class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ("yes_no", "Yes/No"),
        ("scale_1_5", "Scale 1-5"),
        ("text", "Text"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    weight = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text
    




from django.contrib.auth import get_user_model


User = get_user_model()


class QuizAnswer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_answers"
    )

    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    answer = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.question.question_text}"