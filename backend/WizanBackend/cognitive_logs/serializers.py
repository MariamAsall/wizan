from rest_framework import serializers
from .models import CognitiveLog

class CognitiveLogSerializers(serializers.ModelSerializer):

    class Meta:
        model = CognitiveLog
        fields= "__all__"
        read_only_fields= ("user","created_at")

class CognitiveScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField()


class AllowedTaskSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    cognitive_load = serializers.CharField()
    message = serializers.CharField()
    allowed_tasks = serializers.ListField(
        child=serializers.CharField()
    )


class SubmitQuizSerializer(serializers.Serializer):
    answers = serializers.ListField()

class SubmitQuizResponseSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    cognitive_log_id = serializers.IntegerField()


class SkipQuizResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    final_score = serializers.IntegerField()

class CognitiveBriefingSerializer(serializers.Serializer):
    summary = serializers.CharField(required=False)