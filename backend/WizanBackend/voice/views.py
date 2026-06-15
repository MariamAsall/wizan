from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services import transcribe_audio


@api_view(["POST"])
def transcribe_audio(request):
    try:
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response(
                {
                    "success": False,
                    "error": "Audio file is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if audio_file.size == 0:
            return Response(
                {
                    "success": False,
                    "error": "Audio file is empty."
                },
                status=status.HTTP_400_BAD_REQUEST,
                )
        
        allowed_types = [ "audio/webm",
                        "audio/wav",
                        "audio/mpeg",
                        "audio/mp3",
                        "audio/x-wav", 
                        "audio/mp4",
                            ]
        if (
            audio_file.content_type
            not in allowed_types
        ):
            return Response(
                {
                    "success": False, 
                    "error": f"Unsupported format: {audio_file.content_type}" ,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        transcript = transcribe_audio( audio_file )
        if not transcript:
            return Response(
                {
                    "success": False,
                    "error": "No speech detected."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "success": True,
                "transcript": transcript
            })
    except Exception as e:
        print("Transcription Error:", str(e))

        return Response(
            {
                "success": False,
                "error": str(e),
            },
           status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )