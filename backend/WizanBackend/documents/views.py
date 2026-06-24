from django.shortcuts import render

# Create your views here.

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Document
from .services.pdf_extractor import extract_text_from_pdf
from .services.content_guard import guard_document_text, DocumentRejected
from .services.rag import ask_document, suggest_tasks_from_document
from .tasks import process_document_async

from django.shortcuts import get_object_or_404


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=True))
    def post(self, request):
        # filename = request.data.get('filename')
        # raw_text = request.data.get('raw_text')  
        # # أو parse من file

        # doc = Document.objects.create(
        #     user=request.user,
        #     filename=filename,
        #     raw_text=raw_text,
        # )

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "PDF file is required"},
                status=400
            )

        raw_text = extract_text_from_pdf(uploaded_file)

        # Reject the whole upload if the extracted text trips the
        # injection guard. Checked here, before Document.objects.create(),
        # so no DB row and no Celery task are ever created for a
        # rejected file. See content_guard.py for why "reject whole
        # document" was chosen over chunk-level quarantine.
        try:
            guard_document_text(raw_text)
        except DocumentRejected as e:
            return Response(
                {
                    "error": "This document could not be processed.",
                    "detail": "Content flagged by security filter.",
                },
                status=400,
            )

        doc = Document.objects.create(
            user=request.user,
            filename=uploaded_file.name,
            raw_text=raw_text,
        )
        process_document_async.delay(str(doc.id))  # async

        return Response({"id": doc.id, "status": doc.status}, status=201)


class DocumentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        return Response({"id": doc.id, "status": doc.status})


class AskDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
    def post(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)

        if doc.status != 'ready':
            return Response({"error": "Document not ready yet"}, status=400)

        query = request.data.get('query')
        if not query:
             return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
             )
        result = ask_document(query, str(doc.id))
        return Response(result)


class SuggestTasksView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
    def post(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)

        if doc.status != 'ready':
            return Response({"error": "Document not ready yet"}, status=400)

        tasks = suggest_tasks_from_document(str(doc.id))
        return Response({"tasks": tasks})
    
class StudyChatView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "query is required"}, status=400)

        from .services.rag import study_chat
        result = study_chat(query, request.user.id)
        return Response(result)    