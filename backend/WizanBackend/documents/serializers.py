from rest_framework import serializers


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class DocumentStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.CharField()


class AskDocumentSerializer(serializers.Serializer):
    query = serializers.CharField()


class SourceSerializer(serializers.Serializer):
    source = serializers.CharField()
    page = serializers.IntegerField()


class AskDocumentResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = SourceSerializer(many=True)


class SuggestTasksResponseSerializer(serializers.Serializer):
    tasks = serializers.ListField(
        child=serializers.CharField()
    )


class StudyChatRequestSerializer(serializers.Serializer):
    query = serializers.CharField()


class StudyChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = SourceSerializer(many=True)