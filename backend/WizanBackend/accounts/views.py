from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class DeleteMyAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        user = request.user

        user.delete()

        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )