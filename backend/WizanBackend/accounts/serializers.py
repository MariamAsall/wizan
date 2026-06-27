from rest_framework import serializers

class DeleteAccountResponseSerializer(serializers.Serializer):
    message = serializers.CharField()