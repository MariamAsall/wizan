# documents/services/content_guard.py
"""
Injection guard for RAG document ingestion.

WHY THIS EXISTS SEPARATELY FROM ai/middleware/prompt_injection.py:
That middleware inspects request.data (JSON/form fields like "query" or
"message"). A PDF upload arrives as a file, not a text field — by the
time the middleware would see it, it's still just bytes. The actual
injectable text only exists *after* pdf_extractor.py runs. So this check
has to live in the document pipeline itself, not in middleware.

DECISION: reject the whole document, not chunk-level quarantine.
A partially-sanitized study document with silently missing chunks is
worse for a student than a clear upload rejection — gaps in study
material are hard to notice and erode trust in the RAG agent. This
keeps the security posture consistent with the request middleware,
which also blocks outright rather than silently stripping content.

This reuses ai/middleware/detectors.py — no new detection logic, just a
different call site. Pattern-based, no extra LLM/API call, so it doesn't
burn Gemini quota on every upload.
"""

from ai.middleware.detectors import scan_text


class DocumentRejected(Exception):
    """Raised when extracted document text trips the injection guard."""

    def __init__(self, reasons):
        self.reasons = reasons
        super().__init__(f"Document rejected: {reasons}")


def guard_document_text(raw_text: str) -> None:
    """
    Scan full extracted document text before it's persisted or chunked.

    Why scan the whole text at once here, instead of per-chunk?
    Chunking (chunker.py) splits on a fixed token window, which can
    cut an injection phrase in half and let it slip past pattern
    matching on either side of the cut. Scanning the full raw_text
    first, before chunking, avoids that gap entirely.

    Raises DocumentRejected if suspicious content is found.
    Returns None (silently) if the document is clean.
    """
    is_suspicious, reasons = scan_text(raw_text)
    if is_suspicious:
        raise DocumentRejected(reasons)


def guard_chunks(chunks: list[dict]) -> None:
    """
    Secondary check at the chunk level, run inside run_pipeline as
    defense-in-depth — covers any document that reaches the pipeline
    without having passed through guard_document_text first (e.g. a
    future ingestion path, an admin-created Document, a manual retry
    on a row that predates this guard).
    """
    for chunk in chunks:
        is_suspicious, reasons = scan_text(chunk["text"])
        if is_suspicious:
            raise DocumentRejected(reasons)
