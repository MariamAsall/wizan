from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "email",
        "username",
        "role",
        "is_approved",
        "is_active",
    )

    list_filter = (
        "role",
        "is_approved",
        "is_active",
    )

    search_fields = (
        "email",
        "username",
    )

    ordering = ("email",)

    fieldsets = (
        (None, {
            "fields": (
                "email",
                "username",
                "password",
            )
        }),

        ("Permissions", {
            "fields": (
                "role",
                "is_approved",
                "is_active",
                "groups",
                "user_permissions",
            )
        }),

        ("Important dates", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "username",
                "role",
                "password1",
                "password2",
                "is_approved",
                "is_active",

            ),
        }),
    )