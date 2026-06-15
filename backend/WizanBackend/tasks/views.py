from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Task, TaskLog, TaskStep
from .serializers import TaskSerializer, TaskOverrideSerializer
from ai.task_regulator_agent import run_task_regulator
from ai.task_regulator_memory import get_session, save_session
from ai.agents.task_decompose_agent import run_task_decompose_agent
from ai.total_score import calculate_total_score
from ai.task_regulator_tools import get_tasks
from ai.task_regulator_limits import apply_limits
from ai.agents.planning_agent import run_planning_agent




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
        session_id = request.data.get("session_id", None)

        if session_id is None:
            session_id = f"regulate_{user.id}"

        # Step 1: run task regulator agent 
        memory = get_session(session_id)
        result = run_task_regulator(user.id, message, memory, session_id)
        save_session(result["session_id"], result["memory"])

        # Step 2: get score data 
        score_data = calculate_total_score(user, quiz_score=None)

        # Step 3: get tasks and apply limits directly 
        raw_tasks = get_tasks(str(user.id))
        current_score = score_data.get("final_score", 50)
        tagged_tasks, _ = apply_limits(raw_tasks, current_score)

        # Step 4: run planning agent 
        plan = run_planning_agent(
            user_message=message,
            score_data=score_data,
            user=user,
            session_id=f"plan_{user.id}",
            tagged_tasks=tagged_tasks
        )
        # update allowed tasks in DB 
        for task in plan["allowed_tasks"]:
            Task.objects.filter(id=task["id"], user=user).update(status="allowed")
            TaskLog.objects.create(
                task_id=task["id"],
                old_status="pending",
                new_status="allowed",
                reason="Approved by Task Regulator Agent"
            )

        # Step 5: return full plan to frontend 
        return Response({
            "reply": plan["reply"],
            "allowed_tasks": plan["allowed_tasks"],
            "postponed_tasks": plan["postponed_tasks"],
            "session_id": result["session_id"]
        })

    @action(detail=True, methods=['post'], url_path='decompose')
    def decompose(self, request, pk=None):
        task = self.get_object()
        # get cognitive score 
        score_data = calculate_total_score(request.user, quiz_score=None)
        # call the decompose agent 
        result = run_task_decompose_agent(
            task_name=task.name,
            score_data=score_data
        )
        # clear old steps and save new ones 
        TaskStep.objects.filter(task=task).delete()
        for step in result.get("steps", []):
            TaskStep.objects.create(
                task=task,
                step_order=step["order"],
                description=step["description"]
            )
        # return to frontend 
        return Response({
            "task_id": task.id,
            "task_name": task.name,
            "tone": result.get("tone"),
            "estimated_time": result.get("estimated_time"),
            "steps": result.get("steps", [])
        })