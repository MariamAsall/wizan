from rest_framework import serializers
import bleach


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class DocumentStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.CharField()


class AskDocumentSerializer(serializers.Serializer):
    query = serializers.CharField()

    def validate_query(self, value):
        return bleach.clean(
            value,
            tags=[],
            strip=True,
        )


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

    def validate_query(self, value):
        return bleach.clean(
            value,
            tags=[],
            strip=True,
        )


class StudyChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = SourceSerializer(many=True)