from django.db import models
from django.conf import settings
# Create your models here.

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('allowed', 'Allowed'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('overridden', 'Overridden'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    source = models.CharField(max_length=20,default='user_added')
    postponed_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.status})"


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs')
    old_status = models.CharField(max_length=15)
    new_status = models.CharField(max_length=15)
    reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task {self.task.id}: {self.old_status} → {self.new_status}"


class AgentMemory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent_memories')
    session_id = models.CharField(max_length=255)
    memory_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary     = models.TextField()    

    class Meta:
        ordering = ['created_at']     

    def __str__(self):
        return f"Memory for user {self.user.id} - session {self.session_id}   {self.created_at.date()}"

       # newest first


class TaskStep(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='steps')
    step_order = models.PositiveIntegerField()
    description = models.CharField(max_length=500)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_order']

    def __str__(self):
        return f"Step {self.step_order}: {self.description}"