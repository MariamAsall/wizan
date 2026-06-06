from django.urls import path

from .views import(
    CognitiveScoreView,
    AllowedTaskViews,
    CognitiveLogCreateView,
)

urlpatterns = [
    path("cognitive-score/",CognitiveScoreView.as_view()),

    path("allowed-tasks/",AllowedTaskViews.as_view()),

    path("cognitive-log/",CognitiveLogCreateView.as_view()),
]
