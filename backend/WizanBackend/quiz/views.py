# views.py

from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)

from .models import QuizQuestion, QuizAnswer
from .serializers import (
    QuizQuestionSerializer,
    QuizAnswerSerializer,
)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]

        return [IsAuthenticated()]



class QuizAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizAnswer.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )