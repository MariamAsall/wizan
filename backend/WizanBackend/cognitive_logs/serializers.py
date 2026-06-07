from rest_framework import serializers
from .models import CognitiveLog

class CognitiveLogSerializers(serializers.ModelSerializer):

    class Meta:
        model = CognitiveLog
        fields= "__all__"
        read_only_fields= ("user","created_at")