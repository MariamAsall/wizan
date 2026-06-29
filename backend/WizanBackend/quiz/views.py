# views.py

from rest_framework import viewsets
from rest_framework.permissions import ( IsAuthenticated, IsAdminUser,)
from rest_framework.response import Response
from cognitive_logs.models import CognitiveLog

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

    def list(self, request, *args, **kwargs):
        questions = self.get_queryset()
        serializer = self.get_serializer(questions, many=True)

        can_skip = CognitiveLog.objects.filter(
            user=request.user
        ).exists()

        return Response({
            "questions": serializer.data,
            "can_skip": can_skip
        })


class QuizAnswerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuizAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizAnswer.objects.filter(
            user=self.request.user
        ).order_by("-created_at")