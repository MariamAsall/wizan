# ai/filters/pii_filter.py
"""
PII filtering on LLM outputs, using presidio-analyzer.

WHY OUTPUT-SIDE, NOT INPUT-SIDE:
ai/middleware/prompt_injection.py and documents/services/content_guard.py
already cover malicious/injected *input*. This is a different problem:
even with no attack at all, an LLM can leak personal information that
was present in its context and echo it back in a normal, well-intentioned
answer. The highest-risk path in this app is RAG: a student uploads a
PDF (lecture notes, but possibly also a transcript, a letter, anything
with their own or someone else's name/email/phone in it), that text
becomes retrieval context, and ask_document()/study_chat() can quote it
back verbatim in the "answer" field that goes straight to the frontend.

WHY PRESIDIO-ANALYZER SPECIFICALLY (not just regex):
Emails, phone numbers, and credit cards are easy to catch with plain
regex. Names are not — "Khaled mentioned the deadline" has no fixed
pattern. presidio-analyzer's default pipeline uses spaCy NER
(en_core_web_sm) for PERSON/LOCATION entities on top of its own
regex-based recognizers for structured PII (email, phone, IBAN, credit
card, etc.), which is the actual reason to reach for it instead of
writing more regex like detectors.py already has for injection patterns.

ENTITY SCOPE (deliberately narrow, not presidio's full default set):
presidio ships country-specific recognizers (US SSN, UK NINO, IN
Aadhaar, etc.) that aren't relevant to this app's actual data and would
only add false-positive risk. We explicitly scope to the entities that
matter for a student cognitive-load app:
  - PERSON           (names appearing in uploaded docs / agent replies)
  - EMAIL_ADDRESS
  - PHONE_NUMBER
  - LOCATION
  - CREDIT_CARD       (cheap to keep, near-zero false-positive cost)

DATE_TIME was tried and removed. Confirmed twice in real-world testing
(with en_core_web_sm actually installed) that its digit-pattern
heuristic misclassifies plain phone numbers as dates on pure digit
strings — and does so confidently enough that raising its score
threshold only relocated the conflict rather than resolving it. A
leaked date is also the lowest-sensitivity entity on this list on its
own, so dropping it trades very little real protection for removing a
recurring false-positive source.

DEGRADATION IF SPACY MODEL IS MISSING:
en_core_web_sm is fetched from GitHub Releases at build time (see
requirements/Dockerfile note in the integration instructions). If it's
ever missing at runtime (failed download, fresh env not yet set up),
we do NOT want the whole app to crash on every single agent response.
This module catches that specific failure, logs a clear warning once,
and falls back to presidio's regex-only recognizers (email, phone,
credit card still get caught; PERSON/LOCATION NER does not, since that
requires the model). This is a deliberate degrade-not-crash decision —
same posture as ai/llm.py's Gemini→Groq fallback.

ACTION ON DETECTION:
Replace detected spans with a placeholder ("[REDACTED:EMAIL_ADDRESS]"
etc.), not full rejection. Unlike the input-side injection guard, the
right behavior here is different: an LLM reply rejected outright (as
the input guard does) just means the student tries again. An LLM reply
that's *redacted* is just as useful with the personal info masked —
rejecting and discarding the whole answer would be a worse experience
for something as core as "explain what's in my notes."
"""

import logging
import re

logger = logging.getLogger("ai.security.pii_filter")

_analyzer = None
_spacy_model_available = True

# Entities we actually care about for this app — see module docstring.
SCANNED_ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "LOCATION",
    "CREDIT_CARD",
]
# DATE_TIME deliberately excluded. Confirmed twice in real-world
# testing (not just theorized) that its digit-pattern heuristic
# misclassifies plain phone numbers as dates on pure digit strings
# like "01012345678" — and does so with high enough confidence that
# raising its score threshold didn't resolve the conflict, only moved
# it. A leaked date on its own is also the lowest-sensitivity entity
# in this list (rarely identifying by itself, unlike a name, email,
# phone, or card number), so excluding it trades very little real
# protection for removing a recurring, hard-to-tune false-positive
# source.

# Confidence threshold — presidio scores each match 0.0-1.0.
# 0.6 catches solid matches while avoiding the noisiest low-confidence
# guesses (e.g. a capitalized word being flagged PERSON at 0.3).
#
# PHONE_NUMBER is a documented exception: presidio's context-free phone
# recognizer caps out around 0.4-0.5 even on a clearly valid number,
# because it has no surrounding context to raise its own confidence.
# Using the same 0.6 floor for phone numbers as for everything else
# silently drops real matches — confirmed in testing, not a guess — so
# phone numbers get their own lower threshold.
MIN_SCORE = 0.6
PER_ENTITY_MIN_SCORE = {
    "PHONE_NUMBER": 0.35,
}

# Regions relevant to this app's actual userbase (Egypt-based students,
# plus common neighboring/int'l formats). presidio's PhoneRecognizer
# defaults to ('US','UK','DE','FE','IL','IN','CA','BR') — EG is not in
# that list, so without this override Egyptian numbers are missed
# entirely, not just scored low.
PHONE_REGIONS = ("EG", "SA", "AE", "US", "UK")


def _get_analyzer():
    """
    Lazily build and cache the AnalyzerEngine. Lazy so importing this
    module (e.g. for running unit tests on other parts of the codebase)
    doesn't force-load spaCy on every test run.

    IMPORTANT IMPLEMENTATION NOTE:
    We deliberately do NOT let presidio's NlpEngineProvider/SpacyNlpEngine
    resolve the model itself. In testing, when the model is missing,
    presidio's resolution path invokes spaCy's own auto-download
    machinery, which shells out to `pip install` as a subprocess. In a
    locked-down environment (no PyPI access, externally-managed Python,
    restricted egress) that subprocess fails loudly and the failure is
    NOT a normal Python exception — it isn't reliably catchable with
    try/except, and can take the whole process down with it.

    To avoid that entirely, we load the spaCy model ourselves first
    with plain `spacy.load()`, which raises a clean, catchable OSError
    if the model isn't installed and does NOT attempt any download.
    Only if that succeeds do we hand the already-loaded pipeline to
    presidio. If it fails, we skip presidio's NLP-backed engine
    entirely and go straight to the regex-only fallback.
    """
    global _analyzer, _spacy_model_available

    if _analyzer is not None:
        return _analyzer

    import spacy

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError as e:
        logger.warning(
            "spaCy model 'en_core_web_sm' not installed (%s). "
            "Falling back to regex-only PII detection — PERSON/LOCATION "
            "entities will NOT be caught until the model is installed. "
            "Run: python -m spacy download en_core_web_sm",
            e,
        )
        _spacy_model_available = False
        _analyzer = _build_fallback_analyzer()
        return _analyzer

    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    from presidio_analyzer.predefined_recognizers import PhoneRecognizer
    from presidio_analyzer.nlp_engine import SpacyNlpEngine

    nlp_engine = SpacyNlpEngine(models=[{"lang_code": "en", "model_name": "en_core_web_sm"}])
    nlp_engine.nlp = {"en": nlp}  # hand it the already-loaded pipeline directly

    registry = _build_registry()

    try:
        _analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, registry=registry, supported_languages=["en"]
        )
    except Exception as e:
        logger.warning(
            "presidio AnalyzerEngine failed to initialize even with a "
            "loaded spaCy model (%s). Falling back to regex-only PII "
            "detection.",
            e,
        )
        _spacy_model_available = False
        _analyzer = _build_fallback_analyzer()

    return _analyzer


def _build_registry():
    """
    Build a recognizer registry scoped to this app's actual needs:
      - PhoneRecognizer is replaced with one that knows about Egyptian
        (and neighboring) number formats — presidio's default region
        list omits EG entirely, so unmodified it misses Egyptian phone
        numbers outright, not just scores them low.
      - UrlRecognizer is dropped. It's not in SCANNED_ENTITIES (URLs
        aren't PII we care about redacting here), and loading it
        triggers a live network fetch of the public-suffix list on
        first use — an avoidable network dependency and noisy stderr
        traceback when that fetch is blocked, confirmed in testing.
    """
    from presidio_analyzer import RecognizerRegistry
    from presidio_analyzer.predefined_recognizers import PhoneRecognizer

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(languages=["en"])

    # Swap in a region-aware phone recognizer.
    registry.remove_recognizer("PhoneRecognizer")
    registry.add_recognizer(PhoneRecognizer(supported_regions=PHONE_REGIONS))

    # Drop UrlRecognizer — see docstring above.
    registry.remove_recognizer("UrlRecognizer")

    return registry


def _build_fallback_analyzer():
    """
    A presidio AnalyzerEngine that does not depend on a real spaCy
    model being present. Used only if the real NLP model fails to load.

    Why this approach: presidio's NlpEngineProvider, when given a model
    config, will try to actually resolve/load that spaCy model the same
    way the primary path does — so pointing it at "en_core_web_sm" here
    doesn't help if that's exactly what's missing. Instead we explicitly
    use spaCy's blank (no pretrained weights, no download) pipeline,
    which presidio accepts as a valid — if NER-less — backing engine.
    Built-in regex/checksum recognizers (email, phone, credit card,
    IBAN, etc.) still run normally on top of it; only NER-based
    PERSON/LOCATION detection is unavailable in this mode.
    """
    import spacy
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import SpacyNlpEngine

    blank_pipeline = spacy.blank("en")
    nlp_engine = SpacyNlpEngine(models=[{"lang_code": "en", "model_name": "en"}])
    nlp_engine.nlp = {"en": blank_pipeline}

    registry = _build_registry()

    return AnalyzerEngine(nlp_engine=nlp_engine, registry=registry, supported_languages=["en"])


def _resolve_overlaps(results):
    """
    Given a list of presidio RecognizerResult objects, remove
    overlapping matches, keeping only the highest-confidence match in
    each overlapping cluster. Ties broken by longer span (more
    specific match wins over a shorter sub-span).

    Self-contained on purpose: presidio's RecognizerResult exposes
    `intersects`/`contained_in`/`has_conflict` as internal helpers, but
    we don't depend on their exact semantics here — sorting by score
    then greedily rejecting anything that overlaps an already-accepted,
    higher-scoring result is simple enough to verify directly with the
    public start/end/score attributes alone.
    """
    # Highest score first; for ties, longer span first.
    ordered = sorted(
        results, key=lambda r: (r.score, r.end - r.start), reverse=True
    )

    accepted = []
    for candidate in ordered:
        overlaps_accepted = any(
            candidate.start < a.end and a.start < candidate.end
            for a in accepted
        )
        if not overlaps_accepted:
            accepted.append(candidate)

    return accepted


def filter_pii(text: str, language: str = "en") -> str:
    """
    Scan text for PII and replace detected spans with a redaction
    placeholder. Returns the redacted text. Never raises — a filter
    failure should not break the user-facing response; on internal
    error we log and return the original text unchanged.

    Why return text unchanged on error instead of blocking?
    A PII-filter crash blocking the agent's entire reply would be a
    worse outcome than an unfiltered reply getting through. The
    detection logic itself is well-tested (see ai/tests/), so this is
    a safety net for genuinely unexpected failures, not the normal path.
    """
    if not text or not isinstance(text, str):
        return text

    try:
        analyzer = _get_analyzer()
        # Analyze with no score_threshold here — presidio's threshold
        # is applied uniformly across entities, which would either
        # over-filter PHONE_NUMBER or under-filter everything else.
        # We apply per-entity thresholds ourselves below instead.
        results = analyzer.analyze(
            text=text,
            entities=SCANNED_ENTITIES,
            language=language,
        )
    except Exception as e:
        logger.error("PII filter failed, returning text unfiltered: %s", e)
        return text

    results = [
        r
        for r in results
        if r.score >= PER_ENTITY_MIN_SCORE.get(r.entity_type, MIN_SCORE)
    ]

    if not results:
        return text

    # Resolve overlaps BEFORE replacing anything.
    #
    # Real bug found in testing: a single digit string can be matched
    # by two different recognizers with overlapping-but-not-identical
    # spans (e.g. a 16-digit credit card number where presidio's date
    # recognizer also matches a sub-span of it as DATE_TIME). Naively
    # replacing each match independently — even sorted by start
    # position — corrupts the string, because the second replacement's
    # start/end offsets were computed against the ORIGINAL text, not
    # the already-modified text from the first replacement.
    results = _resolve_overlaps(results)

    # Replace longest/highest-confidence spans first so overlapping
    # detections don't corrupt offsets when we splice the string.
    results = sorted(results, key=lambda r: r.start, reverse=True)

    redacted = text
    for result in results:
        placeholder = f"[REDACTED:{result.entity_type}]"
        redacted = redacted[: result.start] + placeholder + redacted[result.end :]

    logger.info(
        "PII filter redacted %d span(s): %s",
        len(results),
        [r.entity_type for r in results],
    )

    return redacted


def spacy_model_available() -> bool:
    """Exposed for health checks / startup diagnostics."""
    _get_analyzer()
    return _spacy_model_available
