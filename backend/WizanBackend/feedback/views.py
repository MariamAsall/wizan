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
    

class FeedbackStatsView(APIView):
    def get(self, request):
        likes = ChatFeedback.objects.filter(rating=1).count()
        dislikes = ChatFeedback.objects.filter(rating=-1).count()

        total = likes + dislikes

        if total > 0:
            like_percentage = round((likes / total) * 100, 2)
            dislike_percentage = round((dislikes / total) * 100, 2)
        else:
            like_percentage = 0
            dislike_percentage = 0

        return Response({
            "likes": likes,
            "dislikes": dislikes,
            "total": total,
            "like_percentage": like_percentage,
            "dislike_percentage": dislike_percentage,
        })