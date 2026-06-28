from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ChatFeedback
from .serializers import ChatFeedbackSerializer


class ChatFeedbackView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChatFeedbackSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        ChatFeedback.objects.create(
            user=request.user,
            question=serializer.validated_data["question"],
            answer=serializer.validated_data["answer"],
            rating=serializer.validated_data["rating"],
        )

        return Response(
            {"message": "Feedback saved"},
            status=status.HTTP_201_CREATED
        )