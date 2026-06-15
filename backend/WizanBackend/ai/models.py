# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class AgentMemory(models.Model):
#     user        = models.ForeignKey(User, on_delete=models.CASCADE)
#     session_id  = models.CharField(max_length=100)
#     summary     = models.TextField()          # the 2-3 line summary LLM writes
#     created_at  = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']            # newest first

#     def __str__(self):
#         return f"{self.user} | {self.session_id} | {self.created_at.date()}"

# ai/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AgentMemory(models.Model):
    """
    Stores 2-3 line SUMMARIES of past sessions.
    Why? So the agent remembers the user's patterns across days.
    Example: "User postponed thesis 3 days in a row."
    """
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    summary    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | {self.session_id} | {self.created_at.date()}"


class AgentSession(models.Model):
    """
    Stores the FULL conversation turns for the planning agent.
    Why separate from AgentMemory?
    AgentMemory  = summary (2-3 lines, kept forever)
    AgentSession = full turns (last 20 messages, rolling window)
    """
    session_id = models.CharField(max_length=100, unique=True)
    user       = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    history    = models.TextField(default="[]")  # stored as JSON
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id}"