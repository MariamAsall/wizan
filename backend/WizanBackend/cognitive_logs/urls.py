from django.urls import path

from .views import(
    CognitiveScoreView,
    AllowedTaskViews,
)

urlpatterns = [
    path("cognitive-score/",CognitiveScoreView.as_view()),

    path("allowed-tasks/",AllowedTaskViews.as_view()),
]
