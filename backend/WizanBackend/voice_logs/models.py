from django.db import models
from django.conf import settings


class VoiceLog(models.Model):
    """
    Logs metadata for each voice interaction.

    RULE: This table NEVER stores audio data.
    Audio is transient — it lives only in memory during the HTTP request
    and is discarded immediately after Samy's STT function returns text.
    What we persist here is the *result* (transcribed text) and *metadata*
    (who, when, what action happened, did it succeed).
    """

    ACTION_TYPES = [
        ("plan_request", "Plan Request"),    # user asked for a daily plan via voice
        ("task_add",     "Task Add"),         # user added a task via voice (future)
        ("query",        "Query"),            # user asked a question via voice (future)
    ]

    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed",  "Failed"),
        ("partial", "Partial"),               # STT worked but planning agent failed
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="voice_logs",
    )

    # What the user said — this is the STT output from SST function.
    # We store it so the team can debug / audit without re-running audio.
    transcribed_text = models.TextField(
        help_text="The text output from Samy's STT function. Never store audio here."
    )

    # The Planning Agent's full reply — stored so frontend
    # can re-fetch it without re-running the agent.
    agent_response = models.TextField(
        blank=True,
        help_text="The daily plan text returned by the Planning Agent."
    )

    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        default="plan_request",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="success",
    )

    # Useful for debugging: which session did the Planning Agent use?
    session_id = models.CharField(max_length=255, blank=True)

    # If anything went wrong, store the reason (never store audio here either).
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"VoiceLog({self.user.email}, {self.action_type}, {self.status}, {self.created_at.date()})"
