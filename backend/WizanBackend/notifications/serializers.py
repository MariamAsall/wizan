from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"

class NotificationCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class UnreadCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()