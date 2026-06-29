from urllib import request

from quiz.models import QuizAnswer, QuizQuestion
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.timezone import localdate

from .models import CognitiveLog
from .serializers import CognitiveLogSerializers,CognitiveScoreSerializer,AllowedTaskSerializer,SubmitQuizSerializer,SubmitQuizResponseSerializer,SkipQuizResponseSerializer,CognitiveBriefingSerializer
from emails.services import send_score_email
from drf_spectacular.utils import extend_schema


@extend_schema(
    responses=CognitiveScoreSerializer,
)
class CognitiveScoreView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CognitiveScoreSerializer

    def get(self, request):
        latest_log = (
            CognitiveLog.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        if not latest_log:
            return Response({"score": 0})

        return Response({
            "score": latest_log.final_score or latest_log.score
        })


@extend_schema(
    responses=AllowedTaskSerializer,
)
class AllowedTaskViews(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AllowedTaskSerializer

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

        score = latest_log.final_score or latest_log.score

        if score >= 60:

            cognitive_load = "LOW"

            message = "User can perform all tasks."

            allowed_tasks = [
                "advanced_task",
                "intermediate_task",
                "basic_task",
            ]

        elif score >= 30:

            cognitive_load = "MEDIUM"

            message = "User should avoid high cognitive load tasks."

            allowed_tasks = [
                "intermediate_task",
                "basic_task",
            ]

        else:

            cognitive_load = "HIGH"

            message = "User should only perform basic tasks."

            allowed_tasks = [
                "basic_task"
            ]

        return Response({
            "score": score,
            "cognitive_load": cognitive_load,
            "message": message,
            "allowed_tasks": allowed_tasks
        })


class CognitiveLogListView(generics.ListAPIView):

    serializer_class = CognitiveLogSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CognitiveLog.objects
            .filter(user=self.request.user)
            .order_by("-created_at")
        )


@extend_schema(
    request=SubmitQuizSerializer,
    responses=SubmitQuizResponseSerializer,
)
class SubmitQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmitQuizSerializer

    def post(self, request):

        today = localdate()

        if CognitiveLog.objects.filter(
            user=request.user,
            log_date=today
        ).exists():

            return Response(
                {"error": "You have already completed the quiz today."},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers = request.data.get("answers", [])

        if not answers:
            return Response(
                {"error": "Answers are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        question_ids = [
            item.get("question_id")
            for item in answers
            if item.get("question_id")
        ]

        if len(question_ids) != len(set(question_ids)):
            return Response(
                {"error": "Duplicate questions are not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        questions_map = {
            str(q.id): q
            for q in QuizQuestion.objects.filter(id__in=question_ids)
        }

        total_score = 0
        max_score = 0

        saved_answers = []
        quiz_answer_objects = []

        for item in answers:

            q_id = str(item.get("question_id"))
            raw_answer = item.get("answer")

            if q_id not in questions_map:
                return Response(
                    {"error": f"Question {q_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )

            question = questions_map[q_id]

            answer_value = str(raw_answer).strip()

            try:

                if question.question_type == "scale_1_5":

                    value = int(answer_value)

                    if not (1 <= value <= 5):
                        return Response(
                            {
                                "error": f"Value for question {q_id} must be between 1 and 5."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    total_score += value * question.weight
                    max_score += 5 * question.weight

                elif question.question_type == "yes_no":

                    if answer_value.lower() not in ["yes", "no"]:
                        return Response(
                            {
                                "error": f"Answer for question {q_id} must be yes or no."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    value = 1 if answer_value.lower() == "yes" else 0

                    total_score += value * question.weight
                    max_score += question.weight

            except (ValueError, TypeError):

                return Response(
                    {"error": f"Invalid answer format for question {q_id}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            quiz_answer_objects.append(
                QuizAnswer(
                    user=request.user,
                    question=question,
                    answer=answer_value
                )
            )

            saved_answers.append({
                "question_en": question.question_text_en,
                "question_ar": question.question_text_ar,
                "answer": answer_value
            })

        score = int((total_score / max_score) * 100) if max_score > 0 else 0

        try:

            with transaction.atomic():

                QuizAnswer.objects.bulk_create(quiz_answer_objects)

                cognitive_log = CognitiveLog.objects.create(
                    user=request.user,
                    score=score,
                    quiz_answers=saved_answers,
                    log_date=today
                )

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        ## send score summary email
        try:
            cognitive_log.refresh_from_db()
            email_score = cognitive_log.final_score or score
            send_score_email(request.user, email_score)
        except Exception:
            pass

        return Response(
            {
                "score": score,
                "cognitive_log_id": cognitive_log.id
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    request=None,
    responses=SkipQuizResponseSerializer,
)
class SkipQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SkipQuizResponseSerializer

    def post(self, request):

        today = localdate()

        if CognitiveLog.objects.filter(
            user=request.user,
            log_date=today
        ).exists():

            return Response(
                {"error": "You already have a score for today."},
                status=status.HTTP_400_BAD_REQUEST
            )

        CognitiveLog.objects.create(
            user=request.user,
            score=None,
            quiz_answers=[],
            log_date=today,
        )

        log = CognitiveLog.objects.filter(
            user=request.user,
            log_date=today
        ).first()

        return Response({
            "message": "Quiz skipped. Score carried forward from yesterday.",
            "final_score": log.final_score,
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    responses=CognitiveBriefingSerializer,
)
class CognitiveBriefingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CognitiveBriefingSerializer

    def get(self, request):

        latest_log = (
            CognitiveLog.objects
            .filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        if not latest_log or not latest_log.final_score:

            return Response(
                {"error": "No score found. Please take the quiz first."},
                status=status.HTTP_404_NOT_FOUND
            )

        from ai.cognitive_agent import run_cognitive_agent

        briefing = run_cognitive_agent(
            user=request.user,
            final_score=latest_log.final_score,
            zone=latest_log.calculation_note,
        )

        return Response(briefing, status=status.HTTP_200_OK)