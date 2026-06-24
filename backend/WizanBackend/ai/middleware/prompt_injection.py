# ai/middleware/prompt_injection.py
"""
Prompt Injection Defense Middleware.

WHERE THIS RUNS:
This sits in Django's middleware stack (see settings.py), so it inspects
every request BEFORE it reaches any view — and therefore before any text
reaches an LLM call in ai/llm.py, ai/cognitive_agent.py,
ai/task_regulator_agent.py, ai/agents/*, or documents/services/rag.py.

SCOPE (deliberately narrow):
We only inspect requests to paths that are known to feed user text into
an LLM. Login, registration, profile updates, etc. never touch Gemini —
scanning them would just create false-positive risk on unrelated fields
(e.g. a bio that happens to contain the word "ignore").

The path list below is built directly from WizanBackend/urls.py +
each app's urls.py / views.py, not guessed:

  /api/auth/...                 -> users          (NOT scanned — no LLM)
  /api/quiz/...                 -> quiz           (NOT scanned — no LLM)
  /api/cognitive-score/         -> cognitive_logs  (NOT scanned — reads, no LLM)
  /api/submit-quiz/             -> cognitive_logs  -> triggers cognitive_agent
  /api/briefing/                -> cognitive_logs  -> cognitive_agent
  /api/tasks/...                -> tasks           -> task_regulator/planning agents
  /api/regulate/                -> tasks           -> uses "message" field
  /api/.../decompose/           -> tasks           -> task_decompose_agent
  /api/add-task-by-voice/       -> tasks           -> transcript fed to Gemini directly
  /api/voice/...                -> voice_logs      -> transcription pipeline
  /api/documents/...            -> documents       -> upload (file, not scanned here)
  /api/documents/<id>/ask/      -> documents       -> "query" field -> RAG
  /api/documents/<id>/plan/     -> documents       -> RAG -> planning
  /api/chat/study/              -> documents       -> "query" field -> RAG chat

NOTE ON FILE UPLOADS:
Document *uploads* (DocumentUploadView) extract raw text from a PDF.
That extracted text can ALSO carry an injection payload, but it doesn't
arrive in request.data as a clean string the same way a chat message
does — it's binary at the HTTP layer. That needs a *separate* check
inside the RAG pipeline itself (documents/services/pipeline.py or
rag.py), scanning extracted text after pdf_extractor.py runs, not here.
This middleware only covers direct text fields submitted by the user.

ACTION ON DETECTION:
Block with 403 + log. See BLOCK_MODE below if you want to switch to
sanitize-and-continue later — it's a one-line change.
"""

import logging

from django.http import JsonResponse

from .detectors import scan_text

logger = logging.getLogger("ai.security.prompt_injection")

# Flip to False to sanitize (strip flagged text) and continue instead of
# blocking outright. Block is the safer default: it's visible, testable,
# and doesn't risk silently mangling user input.
BLOCK_MODE = True

# (path_prefix, [field_names_to_check])
# Only fields that actually reach an LLM call are listed — see the
# views.py trace in the module docstring above.
SCANNED_ROUTES = [
    ("/api/submit-quiz/", ["answers"]),          # quiz free-text -> cognitive_agent
    ("/api/briefing/", ["message"]),
    ("/api/regulate/", ["message"]),
    ("/api/tasks/", ["name", "reason"]),         # covers /override and task CRUD
    ("/api/add-task-by-voice/", ["priority"]),   # transcript itself comes from audio,
                                                  # but manually-typed fields are here
    ("/api/documents/", ["query"]),               # covers .../ask/ and .../plan/
    ("/api/chat/study/", ["query"]),
]


def _matches_scanned_route(path: str):
    for prefix, fields in SCANNED_ROUTES:
        if path.startswith(prefix):
            return fields
    return None


def _extract_text_values(data, fields):
    """
    Pull out string values for the given field names from request.data.
    Handles the case where a field is a list/dict (e.g. quiz 'answers')
    by flattening to strings.
    """
    values = []
    for field in fields:
        if field not in data:
            continue
        value = data[field]
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, (list, tuple)):
            values.extend(v for v in value if isinstance(v, str))
        elif isinstance(value, dict):
            values.extend(v for v in value.values() if isinstance(v, str))
    return values


class PromptInjectionMiddleware:
    """
    Django middleware. Registered in settings.py MIDDLEWARE list.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        fields = _matches_scanned_route(request.path)

        if fields and request.method in ("POST", "PUT", "PATCH"):
            blocked_response = self._scan_request(request, fields)
            if blocked_response:
                return blocked_response

        return self.get_response(request)

    def _scan_request(self, request, fields):
        # DRF parses request.data lazily; for raw Django requests at the
        # middleware layer we read request.POST as a fallback for
        # form-encoded bodies, and rely on request.body for JSON.
        data = self._safe_get_data(request)
        if data is None:
            return None  # can't parse (e.g. multipart file upload) -> skip

        text_values = _extract_text_values(data, fields)

        for text in text_values:
            is_suspicious, reasons = scan_text(text)
            if is_suspicious:
                user_id = getattr(request.user, "id", "anonymous")
                logger.warning(
                    "Prompt injection blocked | path=%s user=%s reasons=%s snippet=%r",
                    request.path,
                    user_id,
                    reasons,
                    text[:200],
                )
                if BLOCK_MODE:
                    return JsonResponse(
                        {
                            "error": "Your input could not be processed.",
                            "detail": "Content flagged by security filter.",
                        },
                        status=403,
                    )
                # sanitize mode placeholder: strip and let the request
                # continue with cleaned text. Left unimplemented on purpose
                # until BLOCK_MODE is actually flipped, to avoid maintaining
                # dead code paths that haven't been tested.

        return None

    def _safe_get_data(self, request):
        import json

        content_type = request.content_type or ""

        if "application/json" in content_type:
            try:
                return json.loads(request.body or b"{}")
            except (ValueError, UnicodeDecodeError):
                return None

        if "multipart/form-data" in content_type:
            # File upload requests (e.g. document upload, voice audio).
            # request.POST still has any non-file fields.
            return request.POST

        if "application/x-www-form-urlencoded" in content_type:
            return request.POST

        return None
