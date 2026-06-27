from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, ChangePasswordSerializer, PasswordResetRequestSerializer,PasswordResetConfirmSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.contrib.auth.models import update_last_login
    

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from emails.services import send_reset_email
from drf_spectacular.utils import extend_schema

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

def get_tokens_for_user(user):
    refresh= RefreshToken.for_user(user)

    refresh["email"]=user.email
    refresh["username"]= user.username
    refresh["role"]= user.role

    return{
        "refresh" : str(refresh),
        "access": str(refresh.access_token),
    }


@extend_schema(
    request=LoginSerializer,
    responses={200: UserProfileSerializer},
)
class LoginView (APIView):
    permission_classes=[AllowAny]
    serializer_class = LoginSerializer

    def post(self,request):
        serializer= LoginSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        user= serializer.validated_data["user"]
        update_last_login(None, user)
        tokens= get_tokens_for_user(user)

        return Response({
            "message":"Login successful",
            "tokens": tokens,
            "user":    UserProfileSerializer(user).data,

        }, status= status.HTTP_200_OK

        )

@extend_schema(
    request=None,
    responses={200: None},
)
class RefreshTokenView(APIView):

    def post(self, request):

        refresh_token = request.data.get("refresh")

        try:
            token = RefreshToken(refresh_token)

            return Response({
                "access": str(token.access_token),
            })

        except TokenError:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

@extend_schema(
    request=None,
    responses={200: None},
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Logged out successfully"
            })

        except TokenError:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            google_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response(
                {"error": "Invalid Google token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = google_info.get("email")
        first_name = google_info.get("given_name", "")
        last_name = google_info.get("family_name", "")
        username = email.split("@")[0]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        )
        tokens = get_tokens_for_user(user)

        return Response({
            "message": "Login successful",
            "tokens": tokens,
            "user": UserProfileSerializer(user).data,
        }, status=status.HTTP_200_OK)




class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user    
    


@extend_schema(
    request=ChangePasswordSerializer,
    responses={200: None},
)
class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PasswordResetRequestSerializer,
    responses={200: None},
)
class PasswordResetRequestView(APIView):

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            send_reset_email(user, token, uid)
        except User.DoesNotExist:
            pass

        return Response({
            "message": "If this email exists, a reset link has been sent."
        }, status=status.HTTP_200_OK)


@extend_schema(
    request=PasswordResetConfirmSerializer,
    responses={200: None},
)
class PasswordResetConfirmView(APIView):

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        token = request.data.get("token")
        uid = request.data.get("uid")
        new_password = request.data.get("new_password")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if not default_token_generator.check_token(user, token):
                return Response(
                    {"error": "Invalid or expired token"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            return Response({
                "message": "Password reset successful"
            }, status=status.HTTP_200_OK)

        except (User.DoesNotExist, ValueError):
            return Response(
                {"error": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST
            )