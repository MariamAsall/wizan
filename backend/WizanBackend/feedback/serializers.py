from rest_framework import serializers


class ChatFeedbackSerializer(serializers.Serializer):

    question = serializers.CharField()

    answer = serializers.CharField()

    rating = serializers.IntegerField()

class FeedbackStatsSerializer(serializers.Serializer):
    likes = serializers.IntegerField()
    dislikes = serializers.IntegerField()
    total = serializers.IntegerField()
    like_percentage = serializers.FloatField()
    dislike_percentage = serializers.FloatField()