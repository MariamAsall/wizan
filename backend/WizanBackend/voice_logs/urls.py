from django.urls import path
from .views import VoicePlanView, VoiceLogListView

urlpatterns = [
    path("voice/plan/", VoicePlanView.as_view(),    name="voice-plan"),
    path("voice/logs/", VoiceLogListView.as_view(), name="voice-logs"),
]
