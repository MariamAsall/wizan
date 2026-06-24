from django.urls import path
from .views import DeleteMyAccountView

urlpatterns = [
    path(
        "me/",
        DeleteMyAccountView.as_view(),
        name="delete-my-account"
    ),
]