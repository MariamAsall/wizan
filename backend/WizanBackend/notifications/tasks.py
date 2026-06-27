from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task
from notifications.services import create_notification


@shared_task
def check_deadlines():
    print("🔥 Checking task deadlines...")

    tomorrow = timezone.now().date() + timedelta(days=1)

    tasks = Task.objects.filter(
        deadline=tomorrow,
        deadline_reminder_sent=False
    )

    print(f"Found {tasks.count()} tasks")

    for task in tasks:

        create_notification(
            user=task.user,
            title="Deadline Reminder ⏰",
            message=f'"{task.name}" is due tomorrow',
            notification_type="warning"
        )

        task.deadline_reminder_sent = True
        task.save()

        print(f"Notification sent for {task.name}")