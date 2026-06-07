from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics


def get_tokens_for_user(user):
    refresh= RefreshToken.for_user(user)

    refresh["email"]=user.email
    refresh["username"]= user.username
    refresh["role"]= user.role

    return{
        "refresh" : str(refresh),
        "access": str(refresh.access_token),
    }

class LoginView (APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer= LoginSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        user= serializer.validated_data["user"]
        tokens= get_tokens_for_user(user)

        return Response({
            "message":"Login successful",
            "tokens": tokens,
            "user":    UserProfileSerializer(user).data,

        }, status= status.HTTP_200_OK

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