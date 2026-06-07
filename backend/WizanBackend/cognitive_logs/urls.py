from django.urls import path

from .views import( CognitiveScoreView, AllowedTaskViews, CognitiveLogListView,   SubmitQuizAPIView,)

urlpatterns = [
    path("cognitive-score/",CognitiveScoreView.as_view()),

    path("allowed-tasks/",AllowedTaskViews.as_view()),

    path("cognitive-log/",CognitiveLogListView.as_view()),

        path("submit-quiz/", SubmitQuizAPIView.as_view(),   name="submit-quiz" ),
]
