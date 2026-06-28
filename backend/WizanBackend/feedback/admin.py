from django.contrib import admin
from .models import ChatFeedback


@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "question",
        "answer",
        "user__email",
    )