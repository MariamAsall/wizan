from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/auth/', include('users.urls')),
    path('api/quiz/', include('quiz.urls')),

    path('api/',include('cognitive_logs.urls')),

    path('api/', include('tasks.urls')),
    
    path('api/voice/', include('voice_logs.urls')),
    path('api/', include('documents.urls')),

    path("api/schema/", SpectacularAPIView.as_view()),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
    ),

    path(
    "api/",
    include("feedback.urls")
),
path(
    "api/users/",
    include("accounts.urls")
),


]