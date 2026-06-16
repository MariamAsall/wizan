from django.urls import path

from .views import transcribe_audio
urlpatterns = [

path( "voice/transcribe/", transcribe_audio, name="transcribe-audio", )

]