from rest_framework import serializers
from .models import Task, TaskLog, AgentMemory


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    logs = TaskLogSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ['status', 'postponed_to', 'created_at']


class TaskOverrideSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)