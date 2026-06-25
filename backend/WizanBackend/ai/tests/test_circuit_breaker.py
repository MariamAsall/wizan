# ai/tests/test_circuit_breaker.py
"""
Tests for ai/resilience/circuit_breaker.py.

Run with: python -m pytest ai/tests/test_circuit_breaker.py -v
(No Django dependency — circuit_breaker.py only uses threading/time.)
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from ai.resilience.circuit_breaker import CircuitBreaker, CLOSED, OPEN, HALF_OPEN


def make_breaker(threshold=3, cooldown=60):
    """Fresh breaker per test — never share gemini_breaker across tests."""
    return CircuitBreaker(name="test", failure_threshold=threshold, cooldown_seconds=cooldown)


class TestClosedState:
    def test_starts_closed(self):
        cb = make_breaker()
        assert cb.state == CLOSED
        assert cb.allow_request() is True

    def test_single_failure_stays_closed(self):
        cb = make_breaker(threshold=3)
        cb.record_failure()
        assert cb.state == CLOSED
        assert cb.allow_request() is True

    def test_success_resets_failure_count(self):
        cb = make_breaker(threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        # Should take a full 3 fresh failures to open now, not just 1 more.
        cb.record_failure()
        assert cb.state == CLOSED


class TestOpeningTheCircuit:
    def test_opens_after_threshold_consecutive_failures(self):
        cb = make_breaker(threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == OPEN

    def test_open_circuit_blocks_requests(self):
        cb = make_breaker(threshold=2, cooldown=60)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == OPEN
        assert cb.allow_request() is False


class TestHalfOpenRecovery:
    def test_transitions_to_half_open_after_cooldown(self):
        cb = make_breaker(threshold=2, cooldown=0.1)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == OPEN

        time.sleep(0.15)
        # allow_request() is what triggers the OPEN -> HALF_OPEN check.
        assert cb.allow_request() is True
        assert cb.state == HALF_OPEN

    def test_half_open_success_closes_circuit(self):
        cb = make_breaker(threshold=2, cooldown=0.1)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.15)
        cb.allow_request()  # moves to HALF_OPEN
        assert cb.state == HALF_OPEN

        cb.record_success()
        assert cb.state == CLOSED
        assert cb.allow_request() is True

    def test_half_open_failure_reopens_circuit(self):
        cb = make_breaker(threshold=2, cooldown=0.1)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.15)
        cb.allow_request()  # moves to HALF_OPEN
        assert cb.state == HALF_OPEN

        cb.record_failure()
        assert cb.state == OPEN
        # And it should block again immediately (cooldown restarted).
        assert cb.allow_request() is False

    def test_still_blocks_before_cooldown_elapses(self):
        cb = make_breaker(threshold=2, cooldown=10)  # long cooldown
        cb.record_failure()
        cb.record_failure()
        assert cb.state == OPEN
        # No sleep — cooldown hasn't elapsed yet.
        assert cb.allow_request() is False
        assert cb.state == OPEN  # still open, didn't prematurely move on


class TestThreadSafety:
    def test_concurrent_failures_dont_corrupt_state(self):
        """
        Not a rigorous concurrency stress test, just a sanity check
        that the lock prevents obviously corrupted counts under
        concurrent access from multiple threads (Django can serve
        requests from a thread pool).
        """
        import threading

        cb = make_breaker(threshold=1000)  # high threshold, won't trip

        def hit_failure():
            for _ in range(50):
                cb.record_failure()

        threads = [threading.Thread(target=hit_failure) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 10 threads * 50 failures each = 500, should match exactly,
        # not be corrupted by race conditions.
        assert cb._consecutive_failures == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
