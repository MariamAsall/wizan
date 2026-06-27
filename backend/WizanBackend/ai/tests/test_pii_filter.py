# ai/tests/test_pii_filter.py
"""
Tests for ai/filters/pii_filter.py.

Run with: python -m pytest ai/tests/test_pii_filter.py -v

IMPORTANT — these tests behave differently depending on whether
en_core_web_sm is installed in the environment running them:

  - If the spaCy model IS installed: PERSON/LOCATION tests should pass
    using real NER.
  - If the spaCy model is NOT installed: the module logs a warning and
    falls back to regex-only detection. EMAIL/PHONE/CREDIT_CARD tests
    still pass (those don't need NER). PERSON/LOCATION tests are
    skipped automatically rather than failed, since failing them would
    incorrectly suggest a code bug rather than a missing optional
    dependency.

This split is intentional and documented in pii_filter.py's module
docstring — the filter degrades gracefully rather than crashing when
the model is absent, and these tests verify both modes rather than
assuming one.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from ai.filters.pii_filter import filter_pii, spacy_model_available


HAS_SPACY_MODEL = spacy_model_available()
skip_if_no_model = pytest.mark.skipif(
    not HAS_SPACY_MODEL,
    reason="en_core_web_sm not installed — PERSON/LOCATION NER unavailable in this env",
)


class TestEmailRedaction:
    def test_email_redacted(self):
        result = filter_pii("Contact me at john.smith@example.com for the notes.")
        assert "john.smith@example.com" not in result
        assert "[REDACTED:EMAIL_ADDRESS]" in result

    def test_multiple_emails_redacted(self):
        result = filter_pii("Email a@test.com or b@test.com.")
        assert "a@test.com" not in result
        assert "b@test.com" not in result


class TestPhoneRedaction:
    """
    Region-aware: PhoneRecognizer is configured with PHONE_REGIONS
    including 'EG' specifically because the default region list omits
    Egypt entirely (confirmed during integration testing) — without
    that override these would NOT be detected, not just scored lower.
    """

    def test_egyptian_international_format_redacted(self):
        result = filter_pii("Call me at +201012345678 tomorrow.")
        assert "+201012345678" not in result
        assert "[REDACTED:PHONE_NUMBER]" in result

    def test_egyptian_local_format_redacted(self):
        result = filter_pii("My number is 01012345678.")
        assert "01012345678" not in result
        assert "[REDACTED:PHONE_NUMBER]" in result


class TestCreditCardRedaction:
    def test_credit_card_redacted(self):
        result = filter_pii("My credit card is 4532015112830366, remember it.")
        assert "4532015112830366" not in result
        assert "[REDACTED:CREDIT_CARD]" in result

    def test_overlapping_detections_dont_corrupt_output(self):
        """
        Regression test for a real bug found in integration testing:
        a 16-digit credit card number was matched by BOTH the
        CREDIT_CARD recognizer and presidio's DATE_TIME recognizer
        (overlapping but non-identical spans over the same digits).
        Naively replacing each match independently — even when sorted
        by start position — corrupted the output, because the second
        replacement's offsets were computed against the original
        string, not the already-modified one. Output looked like:
        "[REDACTED:DATE_TIME]_CARD]" — mangled and still leaking part
        of the original digit sequence.

        The fix resolves overlaps BEFORE any replacement happens,
        keeping only the highest-confidence match per overlapping
        cluster. This test exists so that fix can never silently
        regress.
        """
        text = "My credit card is 4532015112830366, remember it."
        result = filter_pii(text)

        # The full original digit sequence must never survive in any form.
        assert "4532015112830366" not in result

        # No malformed double-tag artifact from the original bug
        # (e.g. "[REDACTED:DATE_TIME]_CARD]" — a stray fragment of a
        # second placeholder bleeding through after corruption).
        assert "DATE_TIME" not in result
        assert result.count("[REDACTED:") <= 1, (
            "overlapping spans over the same digits should collapse to "
            "exactly one redaction, not multiple competing ones"
        )

        # Exactly one clean, well-formed placeholder.
        assert "[REDACTED:CREDIT_CARD]" in result


@skip_if_no_model
class TestPersonRedaction:
    def test_person_name_redacted(self):
        result = filter_pii("Khaled mentioned the deadline is Friday.")
        assert "Khaled" not in result
        assert "[REDACTED:PERSON]" in result


class TestBenignContentPassesThrough:
    def test_normal_study_content(self):
        text = "This is just normal study content about photosynthesis."
        assert filter_pii(text) == text

    def test_normal_arabic_content(self):
        text = "هذا محتوى دراسي عادي عن الخلايا."
        result = filter_pii(text)
        # Should not crash and should not over-redact unrelated content.
        assert result is not None

    def test_empty_string(self):
        assert filter_pii("") == ""

    def test_none_input(self):
        assert filter_pii(None) is None


class TestFilterNeverCrashes:
    """
    The filter must never raise — a filter crash blocking the whole
    agent reply is a worse outcome than an unfiltered reply slipping
    through. See module docstring in pii_filter.py.
    """

    def test_very_long_input_does_not_crash(self):
        text = "Some study notes. " * 5000
        result = filter_pii(text)
        assert result is not None

    def test_non_string_input_does_not_crash(self):
        result = filter_pii(12345)  # not a string
        assert result == 12345  # returned unchanged, no exception


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
