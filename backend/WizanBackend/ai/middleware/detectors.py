# ai/middleware/detectors.py
"""
Pattern-based prompt injection detection.

Why pattern-based instead of an LLM classifier?
- Zero extra API cost / quota usage (we're on Gemini free tier).
- Runs in microseconds, on every request, with no network call.
- Catches the large majority of casual jailbreak/override attempts that
  actually show up in a student capstone threat model.

This is NOT meant to catch a determined, novel adversarial prompt —
no regex layer can. It's a first line of defense that:
  1. Blocks the obvious stuff before it burns an LLM call.
  2. Gives you something concrete to point at for the eval/security
     checklist item ("adversarial defenses").

Each detector returns (is_match: bool, reason: str) so the middleware
can log *why* something was blocked.
"""

import re

# ── 1. Instruction override / role hijack ────────────────────────────────
# "ignore previous instructions", "disregard the system prompt", etc.
OVERRIDE_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above|earlier) instructions",
    r"disregard (all |any |the )?(previous|prior|above|earlier) (instructions|prompt|rules)",
    r"forget (all |any |the )?(previous|prior|above|earlier) (instructions|rules|context)",
    r"new instructions?\s*:",
    r"system\s*prompt\s*:",
    r"you are now\b",
    r"act as (if you are |a )?(?!a student|a helper)",  # "act as X" minus harmless phrasing
    r"pretend (you are|to be)\b",
    r"from now on,? (you|your behavior)",
    r"do not follow (your|the) (rules|instructions|guidelines)",
    r"reveal (your|the) (system prompt|instructions|prompt)",
    r"what (is|are) your (system prompt|instructions)",
    r"\bDAN\b.{0,20}\bmode\b",  # "DAN mode" style jailbreak naming
    r"jailbreak",
]

# ── 2. Fake conversation injection ────────────────────────────────────────
# Attempts to forge a new turn so the model thinks the "system" or
# "assistant" already said something it didn't.
FAKE_TURN_PATTERNS = [
    r"\n\s*(system|assistant|user)\s*:\s*",
    r"<\|?(system|assistant|user)\|?>",
    r"\[\s*(system|assistant|user)\s*\]",
]

# ── 3. Encoded payload smells ─────────────────────────────────────────────
# Long base64-looking blobs are unusual in normal task names / chat
# messages and are a common smuggling technique.
ENCODED_PATTERN = re.compile(r"[A-Za-z0-9+/]{80,}={0,2}")

# ── 4. Excessive length for a "casual" field ──────────────────────────────
# Task names, override reasons, voice transcripts are normally short.
# A 5000-character "task name" is itself a signal, independent of content.
MAX_REASONABLE_LENGTH = 4000


def _compile(patterns):
    return [re.compile(p, re.IGNORECASE) for p in patterns]


_OVERRIDE_RE = _compile(OVERRIDE_PATTERNS)
_FAKE_TURN_RE = _compile(FAKE_TURN_PATTERNS)


def check_override_patterns(text: str):
    for pattern in _OVERRIDE_RE:
        if pattern.search(text):
            return True, f"instruction-override pattern matched: {pattern.pattern}"
    return False, ""


def check_fake_turn_injection(text: str):
    for pattern in _FAKE_TURN_RE:
        if pattern.search(text):
            return True, f"fake conversation-turn pattern matched: {pattern.pattern}"
    return False, ""


def check_encoded_payload(text: str):
    if ENCODED_PATTERN.search(text):
        return True, "long encoded-looking payload detected"
    return False, ""


def check_excessive_length(text: str):
    if len(text) > MAX_REASONABLE_LENGTH:
        return True, f"input length {len(text)} exceeds {MAX_REASONABLE_LENGTH} chars"
    return False, ""


# Order matters only for which "reason" surfaces first in logs.
ALL_CHECKS = [
    check_override_patterns,
    check_fake_turn_injection,
    check_encoded_payload,
    check_excessive_length,
]


def scan_text(text: str):
    """
    Run all checks against a single string.
    Returns (is_suspicious: bool, reasons: list[str]).
    """
    if not text or not isinstance(text, str):
        return False, []

    reasons = []
    for check in ALL_CHECKS:
        matched, reason = check(text)
        if matched:
            reasons.append(reason)

    return (len(reasons) > 0), reasons
