from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Task, TaskLog
from .serializers import TaskSerializer, TaskOverrideSerializer
from ai.task_regulator_agent import run_task_regulator
from ai.task_regulator_memory import get_session, save_session


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='override')
    def override(self, request):
        serializer = TaskOverrideSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_id = serializer.validated_data['task_id']
        reason = serializer.validated_data['reason']

        # boundary score check 
        try:
            from cognitive_logs.models import CognitiveLog
            log = CognitiveLog.objects.filter(user=request.user).latest('created_at')
            score = log.final_score

            if score == 0:
                return Response(
                    {"error": "Override not allowed. Your cognitive load is at maximum. Please rest."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except CognitiveLog.DoesNotExist:
            score = 50

        # get the task 
        try:
            task = Task.objects.get(id=task_id, user=request.user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # only postponed or blocked tasks can be overridden 
        if task.status not in ['postponed', 'blocked']:
            return Response(
                {"error": f"Task is '{task.status}'. Only postponed or blocked tasks can be overridden."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # log the change 
        TaskLog.objects.create(
            task=task,
            old_status=task.status,
            new_status='overridden',
            reason=reason
        )

        # update the task 
        task.status = 'overridden'
        task.save()

        return Response({
            "message": "Task overridden successfully.",
            "task_id": task_id,
            "new_status": "overridden",
            "warning": "You are overriding the agent's recommendation. This may affect your productivity."
        })


    @action(detail=False, methods=['post'], url_path='regulate')
    def regulate(self, request):
        user = request.user
        message = request.data.get("message", "Show me what I can do today")
        session_id = f"regulate_{user.id}"
        memory = get_session(session_id)
        result = run_task_regulator(user.id, message, memory)
        save_session(session_id, result["memory"])
        return Response({"response": result["response"]})