from django.shortcuts import render

from quiz.models import QuizAnswer, QuizQuestion

from rest_framework.views import APIView
from datetime import date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import CognitiveLogSerializers

from .models import CognitiveLog

class CognitiveScoreView(APIView):
    permission_classes= [IsAuthenticated]

    def get(self,request):
        latest_log= CognitiveLog.objects.filter(
            user=request.user).order_by("-created_at").first()
        
        if not latest_log:
            return Response({
                "score": 0
            })
        
        return Response({
            "score": latest_log.score
        })
    

class AllowedTaskViews(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        latest_log= CognitiveLog.objects.filter(
            user=request.user
        ).order_by("-created_at").first()

        if not latest_log:
            return Response({
                "allowed_tasks":[]
            })
        score= latest_log.score

        allowed_tasks=[]

        if score >=80:
            allowed_tasks = [
                "advanced_task",
                "intermediate_task",
                "basic_task",
            ]
        elif score >=50:
            allowed_tasks= [
                "intermediate_task",
                "basic_task",
            ]
        else:
            allowed_tasks= ["basic_task"]

        return Response({
            "score":score,
            "allowed_tasks":allowed_tasks
        })
    
class CognitiveLogCreateView(generics.CreateAPIView):
    serializer_class= CognitiveLogSerializers
    permission_classes=[IsAuthenticated]

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)




class SubmitQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if CognitiveLog.objects.filter(user=request.user,  log_date=date.today()).exists():
            return Response({"error": "You have already completed the quiz today."}, status=status.HTTP_400_BAD_REQUEST)

        answers = request.data.get("answers", [])

        total_score = 0
        max_score = 0

        saved_answers = []

        for item in answers:
            question_id = item.get("question_id")
            answer_value = str(item.get("answer"))

            question = QuizQuestion.objects.get(id=question_id)

            quiz_answer = QuizAnswer.objects.create(user=request.user,question=question,answer=answer_value )

            saved_answers.append({"question": question.question_text,"answer": answer_value})

            if question.question_type == "scale_1_5":
                value = int(answer_value)
                total_score += value * question.weight
                max_score += 5 * question.weight

            elif question.question_type == "yes_no":
                value = 1 if answer_value.lower() == "yes" else 0
                total_score += value * question.weight
                max_score += question.weight

        score = (
            int((total_score / max_score) * 100)
            if max_score > 0   else 0 )

        cognitive_log = CognitiveLog.objects.create(
            user=request.user, score=score, quiz_answers=saved_answers,  log_date=date.today()
        )

        return Response(
            {
                "score": score,
                "cognitive_log_id": cognitive_log.id
            },
            status=status.HTTP_201_CREATED
        )