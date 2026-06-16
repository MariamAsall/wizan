from django.urls import path
from .views import transcribe_audio_api, VoicePlanView, VoiceLogListView

urlpatterns = [
    # خطوة 1: رفع الصوت وتحويله لنص
    path('transcribe/', transcribe_audio_api, name='voice-transcribe'),
    
    # خطوة 2: إرسال النص لتوليد الخطة وحفظ البيانات
    path('plan/', VoicePlanView.as_view(), name='voice-plan'),
    
    # سجل العمليات السابقة
    path('logs/', VoiceLogListView.as_view(), name='voice-logs'),
]
