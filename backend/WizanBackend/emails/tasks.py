from celery import shared_task
from django.contrib.auth import get_user_model
from tasks.models import Task
from .services import send_deadline_reminder

User = get_user_model()

@shared_task
def send_deadline_reminder_task(user_id, task_id):
    try:
        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id)

        if task.status == "postponed":
            return

        send_deadline_reminder(
            user=user,
            task_name=task.name,
            deadline=str(task.deadline),
        )
    except (User.DoesNotExist, Task.DoesNotExist):
        pass