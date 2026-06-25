from rest_framework import serializers


class ChatFeedbackSerializer(serializers.Serializer):

    question = serializers.CharField()

    answer = serializers.CharField()

    rating = serializers.IntegerField()