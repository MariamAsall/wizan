from rest_framework import serializers
from .models import QuizQuestion, QuizAnswer


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = "__all__"


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]