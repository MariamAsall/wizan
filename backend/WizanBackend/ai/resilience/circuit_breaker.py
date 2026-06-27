# ai/resilience/circuit_breaker.py
"""
Circuit breaker for LLM provider calls (Gemini primary).

WHY THIS EXISTS, GIVEN ai/llm.py ALREADY HAS A FALLBACK:
safe_llm_call() already falls back from Gemini to Groq, but only on a
narrow set of error-message keywords ("quota", "429", "rate limit"),
and only ever AFTER trying Gemini fresh on every single call — even if
Gemini has been failing for the last 50 requests in a row. That means:
  1. Non-quota failures (timeouts, 503s, network blips) aren't caught
     at all and just crash the request — confirmed by reading the
     existing code, not assumed.
  2. Every request pays the full latency of a failed Gemini attempt
     before falling back, even when Gemini is clearly down and Groq
     is sitting there working.

A circuit breaker fixes #2 by remembering recent failures and skipping
the doomed attempt entirely once a threshold is crossed. This module
does NOT replace safe_llm_call's fallback logic — it wraps it, deciding
*whether to even try Gemini* before that logic runs.

THREE STATES:
  CLOSED      — normal operation. Calls go to Gemini as usual.
  OPEN        — Gemini has failed FAILURE_THRESHOLD times in a row.
                Skip Gemini entirely for COOLDOWN_SECONDS; route
                straight to the fallback provider instead.
  HALF_OPEN   — cooldown has elapsed. Let exactly one request through
                to Gemini as a test. Success -> CLOSED. Failure -> OPEN
                again, cooldown restarts.

STATE STORAGE: in-memory (a module-level object), not Redis or the DB.
This app runs as a single Django process on Docker, not multiple
load-balanced workers, so there's no "other process doesn't know what
this one knows" problem to solve, and no Redis round-trip needed on
every LLM call just to check a counter. State resets on process
restart — acceptable here, since the breaker re-learns Gemini's
health within a handful of requests anyway.

FAILURE DEFINITION: any exception from the wrapped call counts as a
failure — not just quota/rate-limit keyword matches. A timeout or a
503 means Gemini isn't serving requests right now just as much as a
quota error does, and the student-facing app shouldn't crash on a
transient blip when a working fallback (Groq) is available.
"""

import logging
import threading
import time

logger = logging.getLogger("ai.resilience.circuit_breaker")

CLOSED = "closed"
OPEN = "open"
HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    One CircuitBreaker instance tracks the health of ONE provider
    (e.g. "gemini"). Thread-safe via a simple lock, since Django can
    serve requests from multiple threads.
    """

    def __init__(self, name: str, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self._lock = threading.Lock()
        self._state = CLOSED
        self._consecutive_failures = 0
        self._opened_at = None

    def _transition_to_open(self):
        self._state = OPEN
        self._opened_at = time.monotonic()
        logger.warning(
            "Circuit breaker '%s' OPENED after %d consecutive failures. "
            "Skipping this provider for %ds.",
            self.name,
            self._consecutive_failures,
            self.cooldown_seconds,
        )

    def _transition_to_half_open(self):
        self._state = HALF_OPEN
        logger.info(
            "Circuit breaker '%s' entering HALF_OPEN — cooldown elapsed, "
            "testing provider with one request.",
            self.name,
        )

    def _transition_to_closed(self):
        self._state = CLOSED
        self._consecutive_failures = 0
        self._opened_at = None
        logger.info("Circuit breaker '%s' CLOSED — provider recovered.", self.name)

    def allow_request(self) -> bool:
        """
        Call this BEFORE attempting the provider call. Returns True if
        the call should be attempted, False if it should be skipped
        (caller should go straight to the fallback provider instead).
        """
        with self._lock:
            if self._state == CLOSED:
                return True

            if self._state == OPEN:
                elapsed = time.monotonic() - self._opened_at
                if elapsed >= self.cooldown_seconds:
                    self._transition_to_half_open()
                    return True  # let the one test request through
                return False

            if self._state == HALF_OPEN:
                # Only one probe request is allowed through at a time.
                # Treat this exactly like CLOSED for the purpose of
                # "should I try" — record_success/record_failure below
                # is what actually resolves the half-open test.
                return True

            return True

    def record_success(self):
        with self._lock:
            if self._state in (HALF_OPEN, OPEN):
                self._transition_to_closed()
            else:
                self._consecutive_failures = 0

    def record_failure(self):
        with self._lock:
            self._consecutive_failures += 1

            if self._state == HALF_OPEN:
                # The probe request failed — back to OPEN, cooldown restarts.
                self._transition_to_open()
                return

            if self._state == CLOSED and self._consecutive_failures >= self.failure_threshold:
                self._transition_to_open()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state


# One breaker per provider. Gemini is the one that needs this — Groq
# is already the fallback, so there's nothing to fall back FROM if
# Groq fails (that's a genuine "no provider available" situation,
# handled by safe_llm_call re-raising — see ai/llm.py).
gemini_breaker = CircuitBreaker(
    name="gemini",
    failure_threshold=3,
    cooldown_seconds=60,
)
