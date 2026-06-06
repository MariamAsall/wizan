
# Register your models here.
from django.contrib import admin
from .models import QuizQuestion, QuizAnswer

admin.site.register(QuizQuestion)
admin.site.register(QuizAnswer)