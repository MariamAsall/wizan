from django.shortcuts import render

# Create your views here.

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from drf_spectacular.utils import extend_schema
from rest_framework import serializers

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

import bleach
from audit_logs.utils import log_action
from .serializers import (
    DocumentUploadSerializer,
    DocumentStatusSerializer,
    AskDocumentSerializer,
    AskDocumentResponseSerializer,
    SuggestTasksResponseSerializer,
    StudyChatRequestSerializer,
    StudyChatResponseSerializer,
)


@extend_schema(
    request=DocumentUploadSerializer,
    responses={201: DocumentStatusSerializer},
)
class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentUploadSerializer

    @method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=True))
    def get(self, request):
        docs = Document.objects.filter(user=request.user).order_by('uploaded_at')
        return Response([
            {"id": str(d.id), "filename": d.filename, "status": d.status}
            for d in docs
        ])

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

        log_action(
            request.user,
            f"UPLOAD_DOCUMENT: {uploaded_file.name}"
        )
        process_document_async.delay(str(doc.id))  # async

        return Response({"id": doc.id, "status": doc.status}, status=201)

@extend_schema(
    responses={200: DocumentStatusSerializer},
)
class DocumentStatusView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentStatusSerializer

    def get(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        return Response({"id": doc.id, "status": doc.status})
    
    def delete(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        doc.delete()
        return Response(status=204)



@extend_schema(
    request=AskDocumentSerializer,
    responses={200: AskDocumentResponseSerializer},
)
class AskDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AskDocumentSerializer

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


@extend_schema(
    responses={200: SuggestTasksResponseSerializer},
)
class SuggestTasksView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuggestTasksResponseSerializer

    @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
    def post(self, request, doc_id):
        doc = get_object_or_404(Document, id=doc_id, user=request.user)

        if doc.status != 'ready':
            return Response({"error": "Document not ready yet"}, status=400)

        tasks = suggest_tasks_from_document(str(doc.id))
        return Response({"tasks": tasks})



@extend_schema(
    request=StudyChatRequestSerializer,
    responses={200: StudyChatResponseSerializer},
)  
class StudyChatView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudyChatRequestSerializer

    @method_decorator(ratelimit(key='user_or_ip', rate='15/m', block=True))
    def post(self, request):

        query = request.data.get("query")

        if not query:
            return Response(
                {"error": "query is required"},
                status=400
            )

        query = bleach.clean(
            query,
            tags=[],
            strip=True
        )

        from .services.rag import study_chat

        result = study_chat(
            query,
            request.user.id
        )
        log_action(
            request.user,
            "CHAT_QUERY"
        )

        return Response(result)