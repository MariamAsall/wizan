from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer

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
        }, status= status.HTTP_200_OK

        ),

