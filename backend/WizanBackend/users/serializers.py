from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class LoginSerializer(serializers.Serializer):

    login = serializers.CharField()

    password = serializers.CharField(write_only=True)

    def validate(self, data):

        login = data.get("login")

        password = data.get("password")

        user = User.objects.filter(email=login).first()

        if user:
            auth_user = authenticate(
                email=login,
                password=password
            )
        else:
            try:
                user = User.objects.get(username=login)

                auth_user = authenticate(
                    email=user.email,
                    password=password
                )

            except User.DoesNotExist:
                auth_user = None

        if not auth_user:

            raise serializers.ValidationError(
                "Invalid credentials"
            )

        data["user"] = auth_user

        return data