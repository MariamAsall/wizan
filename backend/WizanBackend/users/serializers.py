from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


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
    

class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="An account with this email already exists.",
        )],
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="This username is already taken.",
        )],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            confirm_password= validated_data['']
            role=validated_data.get("role", "STUDENT")
        )
        return user