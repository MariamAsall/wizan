from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/auth/', include('users.urls')),
    path('api/quiz/', include('quiz.urls')),

    path('api/',include('cognitive_logs.urls')),
    path('api/voice/', include('voice.urls')),

    path('api/', include('tasks.urls')),
    
    path('api/', include('voice_logs.urls')),

]