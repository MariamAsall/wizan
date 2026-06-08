from datetime import date

from quiz.models import QuizAnswer, QuizQuestion

from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CognitiveLog
from .serializers import CognitiveLogSerializers


class CognitiveScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest_log = (
            CognitiveLog.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        if not latest_log:
            return Response({"score": 0})

        return Response({"score": latest_log.score})


class AllowedTaskViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest_log = (
            CognitiveLog.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        if not latest_log:
            return Response({
                "allowed_tasks": []
            })

        score = latest_log.score

        if score >= 80:
            allowed_tasks = [
                "advanced_task",
                "intermediate_task",
                "basic_task",
            ]
        elif score >= 50:
            allowed_tasks = [
                "intermediate_task",
                "basic_task",
            ]
        else:
            allowed_tasks = [
                "basic_task"
            ]

        return Response({
            "score": score,
            "allowed_tasks": allowed_tasks
        })


class CognitiveLogListView(generics.ListAPIView):
    serializer_class = CognitiveLogSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (CognitiveLog.objects.filter(user=self.request.user).order_by("-created_at"))


class SubmitQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if CognitiveLog.objects.filter( user=request.user, log_date=date.today() ).exists():
            return Response({"error": "You have already completed the quiz today."},  status=status.HTTP_400_BAD_REQUEST)

        answers = request.data.get("answers", [])

        if not answers:
            return Response( {"error": "Answers are required."  }, status=status.HTTP_400_BAD_REQUEST)

        question_ids = [ item.get("question_id")
            for item in answers
        ]

        if len(question_ids) != len(set(question_ids)):
            return Response({"error": "Duplicate questions are not allowed." }, status=status.HTTP_400_BAD_REQUEST)

        total_score = 0
        max_score = 0
        saved_answers = []

        for item in answers:
            question_id = item.get("question_id")
            answer_value = str(item.get("answer"))

            try:
                question = QuizQuestion.objects.get(id=question_id)
            except QuizQuestion.DoesNotExist:
                return Response({"error": f"Question {question_id} does not exist."},status=status.HTTP_404_NOT_FOUND)

            QuizAnswer.objects.create(
                user=request.user,
                question=question,
                answer=answer_value
            )

            saved_answers.append({
                "question_en": question.question_text_en,
                "question_ar": question.question_text_ar,
                "answer": answer_value
            })

            if question.question_type == "scale_1_5":
                value = int(answer_value)
                total_score += value * question.weight
                max_score += 5 * question.weight

            elif question.question_type == "yes_no":
                value = (
                    1
                    if answer_value.lower() == "yes"
                    else 0
                )

                total_score += value * question.weight
                max_score += question.weight

        score = (
            int((total_score / max_score) * 100)
            if max_score > 0
            else 0
        )

        cognitive_log = CognitiveLog.objects.create(
            user=request.user,
            score=score,
            quiz_answers=saved_answers,
            log_date=date.today()
        )

        return Response(
            {
                "score": score,
                "cognitive_log_id": cognitive_log.id
            },
            status=status.HTTP_201_CREATED
        )