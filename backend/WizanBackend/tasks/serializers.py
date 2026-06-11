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


class TaskOverrideSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)


