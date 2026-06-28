from django.contrib import admin

from .models import CognitiveLog

@admin.register(CognitiveLog)
class CognitiveLogAdmin(admin.ModelAdmin):
    
    list_display= (
        "id",
        "user",
        "score",
        "log_date",
        "created_at",

    )
    search_fields= (
        "user__email",
        "user__username",
    )
    list_filter= (
        "log_date",
        "created_at",
    )
    