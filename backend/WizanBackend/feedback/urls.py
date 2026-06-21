from django.urls import path
from .views import ChatFeedbackView

urlpatterns = [
    path(
        "chat/feedback/",
        ChatFeedbackView.as_view(),
        name="chat-feedback"
    ),
]