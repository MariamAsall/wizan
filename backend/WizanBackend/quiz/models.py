from django.db import models

# Create your models here.
import uuid


class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ("yes_no", "Yes/No"),
        ("scale_1_5", "Scale 1-5"),
        ("text", "Text"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    question_text_en = models.CharField(max_length=255)
    question_text_ar = models.CharField(max_length=255)

    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    weight = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text_en




from django.contrib.auth import get_user_model


User = get_user_model()


class QuizAnswer(models.Model):
    id = models.UUIDField( primary_key=True, default=uuid.uuid4,  editable=False)

    user = models.ForeignKey( User,  on_delete=models.CASCADE,  related_name="quiz_answers")

    question = models.ForeignKey(   QuizQuestion,  on_delete=models.CASCADE,  related_name="answers" )

    answer = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.question.question_text_en}"