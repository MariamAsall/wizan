from django.urls import path
from .views import DocumentUploadView, DocumentStatusView, AskDocumentView, SuggestTasksView, StudyChatView


urlpatterns = [
    path('documents/',                    DocumentUploadView.as_view()),
    path('documents/<uuid:doc_id>/',      DocumentStatusView.as_view()),
    path('documents/<uuid:doc_id>/ask/',  AskDocumentView.as_view()),
    path('documents/<uuid:doc_id>/plan/', SuggestTasksView.as_view()),
    path('chat/study/',                   StudyChatView.as_view()),
]