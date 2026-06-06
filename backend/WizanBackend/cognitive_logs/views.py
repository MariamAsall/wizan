from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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