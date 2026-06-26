from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from .models import Task, TaskLog, TaskStep
from .serializers import TaskSerializer, TaskOverrideSerializer
from ai.task_regulator_agent import run_task_regulator
from ai.task_regulator_memory import get_session, save_session
from ai.agents.task_decompose_agent import run_task_decompose_agent
from ai.total_score import calculate_total_score
from ai.task_regulator_tools import get_tasks
from ai.task_regulator_limits import apply_limits
from ai.agents.planning_agent import run_planning_agent
from datetime import datetime, timedelta, time 
from django.utils import timezone

# deadline reminder helper function
def schedule_deadline_reminder(task, user):
    if not task.deadline:
        return

    from emails.tasks import send_deadline_reminder_task

    reminder_dt = datetime.combine(task.deadline, time.min) - timedelta(hours=24)
    reminder_dt = timezone.make_aware(reminder_dt)
    now = timezone.now()

    if reminder_dt <= now:
        return

    countdown = int((reminder_dt - now).total_seconds())
    send_deadline_reminder_task.apply_async(
        args=[user.id, task.id],
        countdown=countdown
    )

from notifications.services import create_notification


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        schedule_deadline_reminder(task, self.request.user)

        task = serializer.save(user=self.request.user)

        create_notification(
        user=self.request.user,
        title="New Task Created ✅",
        message=f"Task '{task.name}' was created successfully",
        notification_type="success"
    )
        
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

        create_notification(
        user=request.user,
        title="Task Overridden ⚠️",
        message=f"{task.name} status changed to overridden",
        notification_type="warning"
)

        return Response({
            "message": "Task overridden successfully.",
            "task_id": task_id,
            "new_status": "overridden",
            "warning": "You are overriding the agent's recommendation. This may affect your productivity."
        })


    @action(detail=False, methods=['post'], url_path='regulate')
    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
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

        create_notification(
            user=user,
            title="Tasks Updated by AI 🧠",
            message="Your task schedule was optimized based on your cognitive score",
            notification_type="ai"
)
        # Step 5: return full plan to frontend 
        return Response({
            "reply": plan["reply"],
            "allowed_tasks": plan["allowed_tasks"],
            "postponed_tasks": plan["postponed_tasks"],
            "session_id": result["session_id"]
        })

    @action(detail=True, methods=['post'], url_path='decompose')
    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
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
    


# --------------------  task voice  -------------------- 


import json


from rest_framework.views import APIView

from voice_logs.services import transcribe_audio as transcribe_audio_service

# استيراد جينيريتور الـ AI (Gemini) لاستخراج البيانات منظمّة
from google import genai
from django.conf import settings
from voice_logs.services import structure_with_ai

gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
class VoiceAddTaskView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
    def post(self, request):
        try:
            # 1. التحقق من التاريخ القادم من الـ Frontend يدوياً لمنع التواريخ القديمة وتحويله لكائن تاريخ
            deadline_str = request.data.get("deadline")
            validated_deadline_date = None

            if deadline_str:
                try:
                    validated_deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                    if validated_deadline_date < timezone.localdate():
                        return Response(
                            {"success": False, "error": "The deadline cannot be in the past."}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except ValueError:
                    return Response(
                        {"success": False, "error": "Invalid date format. Expected YYYY-MM-DD."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 2. استقبال ملف الصوت وتفريغه لنص
            audio_file = request.FILES.get("audio")
            if not audio_file or audio_file.size == 0:
                return Response({"success": False, "error": "Invalid audio file."}, status=status.HTTP_400_BAD_REQUEST)

            transcript = transcribe_audio_service(audio_file)
            if not transcript:
                return Response({"success": False, "error": "No speech detected."}, status=status.HTTP_400_BAD_REQUEST)

            # 3. قراءة البيانات اليدوية الأخرى إن وجدت
            frontend_priority = request.data.get("priority")

            # 4. استخدام توقيت دجانجو المحلي لضمان دقة حسابات الـ AI
            today_date = timezone.localdate().strftime("%Y-%m-%d")
            
            prompt = f"""
            You are a task management assistant. Analyze the user's spoken task in Arabic and extract:
            1. 'name': The clean core task title in Arabic (remove urgency words like 'ضروري' or 'بسرعة').
            2. 'priority': Must be one of ['high', 'medium', 'low'] based on the urgency or words used. Default is 'medium'.
            3. 'deadline': The date in YYYY-MM-DD format. Today's date is {today_date}. If they say 'بكرة' calculate tomorrow's date. If no date mentioned, return null.

            Return ONLY a valid JSON object with keys: "name", "priority", "deadline". No markdown wrappers, no backticks.
            User Text: "{transcript}"
            """

            extracted_data = structure_with_ai(prompt)

            if not isinstance(extracted_data, dict):
                extracted_data = {}

            # 5. دمج البيانات المستخرجة
            final_name = extracted_data.get("name") or transcript
            final_priority = frontend_priority or extracted_data.get("priority") or "medium"
            ai_deadline = extracted_data.get("deadline")

            # تحديد التاريخ النهائي والتأكد من تحويله بالكامل إلى كائن date وليس str
            final_deadline_obj = validated_deadline_date

            if not final_deadline_obj and ai_deadline:
                try:
                    ai_deadline_clean = str(ai_deadline).strip()
                    if ai_deadline_clean.lower() not in ['null', 'none', '']:
                        parsed_date = datetime.strptime(ai_deadline_clean, "%Y-%m-%d").date()
                        if parsed_date >= timezone.localdate():
                            final_deadline_obj = parsed_date
                except (ValueError, TypeError):
                    final_deadline_obj = None

            # 6. حفظ المهمة بالبيانات المدمجة والآمنة (نمرر كائن التاريخ الحقيقي هنا)
            new_task = Task.objects.create(
                user=request.user,
                name=final_name,
                priority=final_priority,
                deadline=final_deadline_obj, # كائن من نوع datetime.date أو None
                status='pending',
                source='user_added'
            )
            
            # الآن دالة التذكير ستعمل بنجاح دون أي خطأ في الـ combine
            schedule_deadline_reminder(new_task, request.user)
            
            create_notification(
                user=request.user,
                title="New Voice Task 🎤",
                message=f"'{final_name}' was added successfully",
                notification_type="success"
            )

            serializer = TaskSerializer(new_task)
            return Response({
                "success": True,
                "message": "Task processed and added!",
                "task": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Voice Task Structuring Error:", str(e))
            return Response(
                {"success": False, "error": "Failed to understand task details."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )