
from urllib import request

from quiz.models import QuizAnswer, QuizQuestion
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.timezone import localdate 
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
        

        # score = latest_log.score
        score = latest_log.final_score or latest_log.score  # fallback to score if final not set  (aml)

        if score >= 60:
            allowed_tasks = [
                "advanced_task",
                "intermediate_task",
                "basic_task",
            ]
        elif score >= 30:
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
            "cognitive_load": cognitive_load,
            "message": message,
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
        today = localdate()

        if CognitiveLog.objects.filter(user=request.user, log_date=today).exists():
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

            # ✅ important: inside loop
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

        except Exception:
            return Response(
                {"error": "Failed to save quiz data. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "score": score,
                "cognitive_log_id": cognitive_log.id
            },
            status=status.HTTP_201_CREATED
        )
    

    # backend/WizanBackend/cognitive_logs/views.py
# ADD these two views at the bottom — touch nothing above

class SkipQuizAPIView(APIView):
    """
    User skips quiz today.
    Carries yesterday's score forward with a small decay.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = localdate()

        # don't allow skip if they already submitted today
        if CognitiveLog.objects.filter(
            user=request.user,
            log_date=today
        ).exists():
            return Response(
                {"error": "You already have a score for today."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create log with no score — signal handles decay
        CognitiveLog.objects.create(
            user=request.user,
            score=None,
            quiz_answers=[],
            log_date=today,
        )

        # read the final_score the signal just calculated
        log = CognitiveLog.objects.filter(
            user=request.user,
            log_date=today
        ).first()

        return Response({
            "message": "Quiz skipped. Score carried forward from yesterday.",
            "final_score": log.final_score,
        }, status=status.HTTP_201_CREATED)


class CognitiveBriefingView(APIView):
    """
    Returns AI briefing for the user based on their final_score.
    Frontend calls this after quiz submission to get the AI response.
    """
    permission_classes = [IsAuthenticated]

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

        # import here to avoid circular imports at module level
        from ai.cognitive_agent import run_cognitive_agent

        briefing = run_cognitive_agent(
            user=request.user,
            final_score=latest_log.final_score,
            zone=latest_log.calculation_note,
        )

        return Response(briefing, status=status.HTTP_200_OK)