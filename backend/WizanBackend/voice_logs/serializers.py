from rest_framework import serializers
from .models import VoiceLog


class VoiceInputSerializer(serializers.Serializer):
    """
    What the frontend (or STT pipeline) sends to backend.
    The transcribed_text is the ONLY required field —
    audio never crosses this boundary.
    """
    transcribed_text = serializers.CharField(
        min_length=1,
        max_length=5000,
        help_text="Plain text output from the STT function. No audio blobs.",
    )
    session_id = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional: pass the session_id from a previous turn to continue the conversation.",
    )


class VoiceLogSerializer(serializers.ModelSerializer):
    """Read-only serializer used to return log data to the frontend."""
    class Meta:
        model = VoiceLog
        fields = [
            "id",
            "action_type",
            "status",
            "transcribed_text",
            "agent_response",
            "session_id",
            "created_at",
        ]
        read_only_fields = fields


class TranscribeResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    transcript = serializers.CharField()


class VoicePlanResponseSerializer(serializers.Serializer):
    plan = serializers.CharField()
    session_id = serializers.CharField()
    voice_log_id = serializers.IntegerField()
    score_context = serializers.DictField()