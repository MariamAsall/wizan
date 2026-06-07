# urls.py

from rest_framework.routers import DefaultRouter
from .views import (
    QuizQuestionViewSet,
    QuizAnswerViewSet
)

router = DefaultRouter()

router.register( "questions",  QuizQuestionViewSet)

router.register("answers", QuizAnswerViewSet, basename="answers")

urlpatterns = router.urls