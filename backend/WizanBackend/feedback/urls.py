from django.urls import path
from .views import ChatFeedbackView,FeedbackStatsView

urlpatterns = [
    path(
        "chat/feedback/",
        ChatFeedbackView.as_view(),
        name="chat-feedback"
    ),
    path("chat/feedback/stats/", FeedbackStatsView.as_view()),
]