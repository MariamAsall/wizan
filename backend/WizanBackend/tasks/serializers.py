from datetime import date 
from rest_framework import serializers
from .models import Task, TaskLog, AgentMemory, TaskStep


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = "__all__"

class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = "__all__"
        read_only_fields = ['step_order', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    logs = TaskLogSerializer(many=True, read_only=True)
    steps = TaskStepSerializer(many=True, read_only=True)
   
    class Meta:
            model = Task
            fields = "__all__"
            read_only_fields = [
                "user",
                "status",
                "postponed_to",
                "created_at",
            ]

    def validate_deadline(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

class TaskOverrideSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)


class TaskRegulateRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    session_id = serializers.CharField(required=False, allow_blank=True)


class TaskRegulateResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    allowed_tasks = TaskSerializer(many=True)
    postponed_tasks = TaskSerializer(many=True)
    session_id = serializers.CharField()


class TaskDecomposeResponseSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    task_name = serializers.CharField()
    tone = serializers.CharField()
    estimated_time = serializers.CharField()
    steps = serializers.ListField(
        child=serializers.DictField()
    )


class VoiceTaskResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    task = TaskSerializer()


