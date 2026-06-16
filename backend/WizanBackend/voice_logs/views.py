import uuid

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from cognitive_logs.models import CognitiveLog
from ai.agents.planning_agent import run_planning_agent
from .models import VoiceLog
from .serializers import VoiceInputSerializer, VoiceLogSerializer


def _get_score_data_for_user(user):
    """
    Fetch the latest cognitive score for this user and shape it into the
    score_data dict that run_planning_agent expects.

    Falls back to safe defaults if the user hasn't taken a quiz yet today.
    """
    latest_log = (
        CognitiveLog.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if not latest_log or not latest_log.final_score:
        # No score yet — use neutral defaults so the agent still responds.
        return {
            "final_score":   50,
            "score":         50,
            "zone":          "medium_load",
            "label":         "Medium Cognitive Load",
            "tone":          "calm",
            "allowed_tasks": 3,
            "is_first_time": True,
        }

    score = latest_log.final_score
    note  = latest_log.calculation_note or ""

    if score <= 30:
        zone, label, tone, allowed = "high_load",   "High Cognitive Load",   "gentle",    1
    elif score <= 60:
        zone, label, tone, allowed = "medium_load", "Medium Cognitive Load", "calm",      3
    else:
        zone, label, tone, allowed = "low_load",    "Low Cognitive Load",    "energetic", 5

    return {
        "final_score":   score,
        "score":         score,
        "zone":          zone,
        "label":         label,
        "tone":          tone,
        "allowed_tasks": allowed,
        "is_first_time": "first_time" in note,
    }


class VoicePlanView(APIView):
    """
    POST /api/voice/plan/

    Step 1 — receive the transcribed text from  STT function.
    Step 2 — route the text directly to the Planning Agent 
    Step 3 — return the agent's daily plan text to frontend pipeline.

    No audio is ever read, stored, or passed anywhere in this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ── Validate input ────────────────────────────────────────────────────
        serializer = VoiceInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transcribed_text = serializer.validated_data["transcribed_text"]
        session_id       = serializer.validated_data.get("session_id") or \
                           f"voice_{request.user.id}_{uuid.uuid4().hex[:8]}"

        # ── Get the user's current cognitive score ────────────────────────────
        score_data = _get_score_data_for_user(request.user)

        # ── Step 2: Route text straight to the Planning Agent ─────────────────
        # This is the Arabic requirement:
        #   text  directly to the Planning Agent
        # run_planning_agent accepts (user_message, score_data, user, session_id)
        try:
            agent_reply = run_planning_agent(
                user_message=transcribed_text,
                score_data=score_data,
                user=request.user,
                session_id=session_id,
            )
            log_status = "success"
            error_msg  = ""
        except Exception as exc:
            agent_reply = ""
            log_status  = "partial"
            error_msg   = str(exc)

        # ── Log the interaction (metadata only, no audio) ─────────────────────
        voice_log = VoiceLog.objects.create(
            user             = request.user,
            transcribed_text = transcribed_text,
            agent_response   = agent_reply,
            action_type      = "plan_request",
            status           = log_status,
            session_id       = session_id,
            error_message    = error_msg,
        )

        if log_status == "partial":
            return Response(
                {
                    "error":      "Planning Agent failed. Transcription was saved.",
                    "detail":     error_msg,
                    "voice_log_id": voice_log.id,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # ── Step 3: Return the plan to frontend pipeline ────────────
        # Payload shape is deliberately simple so Mohamed can consume it
        # without any transformation: just read `plan` and render it.
        return Response(
            {
                "plan":         agent_reply,       # ← the daily plan text
                "session_id":   session_id,        # ← send back so frontend can continue the conversation
                "voice_log_id": voice_log.id,      # ← for debugging / audit trail
                "score_context": {
                    "final_score":   score_data["final_score"],
                    "zone":          score_data["zone"],
                    "allowed_tasks": score_data["allowed_tasks"],
                },
            },
            status=status.HTTP_200_OK,
        )


class VoiceLogListView(APIView):
    """
    GET /api/voice/logs/

    Returns the last 20 voice interactions for the current user.
    Read-only — for the frontend history panel or debugging.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = VoiceLog.objects.filter(user=request.user)[:20]
        return Response(VoiceLogSerializer(logs, many=True).data)
