from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password



from .models import User
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
        model  = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "date_of_birth",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name":  {"required": True},
        }

    def validate_username(self, value: str) -> str:
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        if not value.isalnum():
            raise serializers.ValidationError(
                "Username may only contain letters and numbers."
            )
        return value

    def validate_first_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("First name cannot be blank.")
        return value.strip()

    def validate_last_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be blank.")
        return value.strip()

    def validate_phone_number(self, value: str) -> str:
        if value and not value.lstrip("+").isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits (optionally prefixed with '+')."
            )
        return value
    
    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        if attrs.get("role") == User.Role.ADMIN:
            raise serializers.ValidationError(
                {"role": "Admin accounts cannot be created via registration."}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.is_approved = True
        user.is_active   = True
        user.save()

       
        return user

class LoginSerializer(serializers.Serializer):

    email    = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs: dict) -> dict:
        from django.contrib.auth import authenticate

        email    = attrs.get("email", "").strip().lower()
        password = attrs.get("password", "")

        if not email or not password:
            raise serializers.ValidationError(
                "Both email and password are required."
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password. Please try again."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Your account has been deactivated. Contact support."
            )
        if not user.is_approved:
            raise serializers.ValidationError(
                "Your account is pending admin approval."
            )

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "is_approved",
            "date_joined",
        ]
        read_only_fields = fields   # always read-only

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name()


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "profile_picture",
        ]

    def validate_phone_number(self, value: str) -> str:
        if value and not value.lstrip("+").isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits (optionally prefixed with '+')."
            )
        return value

class ChangePasswordSerializer(serializers.Serializer):


    old_password     = serializers.CharField(write_only=True, required=True)
    new_password     = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."}
            )
        return attrs

    def save(self, **kwargs) -> None:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()