from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AgentMemory(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id  = models.CharField(max_length=100)
    summary     = models.TextField()          # the 2-3 line summary LLM writes
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']            # newest first

    def __str__(self):
        return f"{self.user} | {self.session_id} | {self.created_at.date()}"