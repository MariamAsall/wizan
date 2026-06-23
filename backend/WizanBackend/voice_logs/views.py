import uuid
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

# استيراد النماذج والـ Serializers
from cognitive_logs.models import CognitiveLog
from ai.agents.planning_agent import run_planning_agent
from .models import VoiceLog
from .serializers import VoiceInputSerializer, VoiceLogSerializer

# حل مشكلة التضارب: استيراد خدمة التفريغ الصوتي باسم مستعار واضح
from .services import transcribe_audio as transcribe_audio_service


def _get_score_data_for_user(user):
    """
    Fetch the latest cognitive score for this user and shape it into the
    score_data dict that run_planning_agent expects.
    """
    latest_log = (
        CognitiveLog.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if not latest_log or not latest_log.final_score:
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


@api_view(["POST"])
@permission_classes([IsAuthenticated]) # تأمين الـ STT أيضاً لربطه بالمستخدم مستقبلاً إن لزم الأمر
@ratelimit(key='user_or_ip', rate='10/m', block=True)
def transcribe_audio_api(request): # تغيير اسم الدالة لمنع التعارض تماماً
    """
    POST /api/voice/transcribe/
    المرحلة الأولى: استقبال ملف الصوت وتفريغه إلى نص فقط دون معالجة العميل الذكي.
    """
    try:
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response(
                {"success": False, "error": "Audio file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if audio_file.size == 0:
            return Response(
                {"success": False, "error": "Audio file is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        allowed_types = [
            "audio/webm", "audio/wav", "audio/mpeg",
            "audio/mp3", "audio/x-wav", "audio/mp4"
        ]
        if audio_file.content_type not in allowed_types:
            return Response(
                {"success": False, "error": f"Unsupported format: {audio_file.content_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # استدعاء الخدمة المستوردة باسمها الجديد لمنع الـ Loop اللانهائي
        transcript = transcribe_audio_service(audio_file)
        
        if not transcript:
            return Response(
                {"success": False, "error": "No speech detected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        return Response({
            "success": True,
            "transcript": transcript
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("Transcription Error:", str(e))
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class VoicePlanView(APIView):
    """
    POST /api/voice/plan/
    المرحلة الثانية: استقبال النص الجاهز، تمريره للـ Agent، وحفظ السجل.
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
    def post(self, request):
        serializer = VoiceInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transcribed_text = serializer.validated_data["transcribed_text"]
        session_id       = serializer.validated_data.get("session_id") or \
                           f"voice_{request.user.id}_{uuid.uuid4().hex[:8]}"

        score_data = _get_score_data_for_user(request.user)

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

        return Response(
            {
                "plan":         agent_reply,
                "session_id":   session_id,
                "voice_log_id": voice_log.id,
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
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = VoiceLog.objects.filter(user=request.user)[:20]
        return Response(VoiceLogSerializer(logs, many=True).data)