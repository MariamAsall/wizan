from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import DeleteAccountResponseSerializer
from drf_spectacular.utils import extend_schema

User = get_user_model()


from django.utils import timezone

@extend_schema(
    request=None,
    responses={200: DeleteAccountResponseSerializer},
)
class DeleteMyAccountView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteAccountResponseSerializer

    def delete(self, request):
        user = request.user

        user.is_deleted = True
        user.is_active = False
        user.deleted_at = timezone.now()
        user.save()

        return Response(
            {"message": "Account deactivated successfully"},
            status=status.HTTP_200_OK
        )