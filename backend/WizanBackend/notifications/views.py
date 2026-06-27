from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer,NotificationCountSerializer,SuccessSerializer,UnreadCountSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(
    responses=NotificationSerializer(many=True),
)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        )
    
@extend_schema(
    responses=NotificationCountSerializer,
)
class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationCountSerializer

    def get(self, request):

        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({
            "unread_count": count
        })
    
@extend_schema(
    request=None,
    responses=SuccessSerializer,
)
class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuccessSerializer

    def post(self, request, pk):

        notification = Notification.objects.get(
            id=pk,
            user=request.user
        )

        notification.is_read = True
        notification.save()

        return Response({
            "success": True
        })
    
@extend_schema(
    request=None,
    responses=SuccessSerializer,
)
class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuccessSerializer

    def post(self, request):

        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "success": True
        })
    
@extend_schema(
    responses=UnreadCountSerializer,
)
class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnreadCountSerializer

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({
            "count": count
        })
    

class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.delete()
            return Response({
                "success": True, 
                "message": "Notification deleted successfully."
            }, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({
                "success": False, 
                "error": "Notification not found."
            }, status=status.HTTP_404_NOT_FOUND)
