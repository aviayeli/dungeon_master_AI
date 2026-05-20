"""Unit tests for src/watchdog.py — timeout and success paths."""
from __future__ import annotations
import time
import pytest
from src.watchdog import Watchdog, WatchdogTimeoutError


def test_watchdog_returns_result_on_success():
    wd = Watchdog(timeout_sec=5.0)
    assert wd.run(lambda: 42) == 42


def test_watchdog_propagates_string_result():
    wd = Watchdog(timeout_sec=5.0)
    assert wd.run(lambda: "תגובה") == "תגובה"


def test_watchdog_raises_watchdog_timeout_error_on_slow_fn():
    wd = Watchdog(timeout_sec=0.1)
    with pytest.raises(WatchdogTimeoutError):
        wd.run(lambda: time.sleep(2))


def test_watchdog_timeout_error_is_subclass_of_timeout_error():
    wd = Watchdog(timeout_sec=0.1)
    with pytest.raises(TimeoutError):
        wd.run(lambda: time.sleep(2))


def test_watchdog_error_message_mentions_seconds():
    wd = Watchdog(timeout_sec=0.1)
    with pytest.raises(WatchdogTimeoutError) as exc_info:
        wd.run(lambda: time.sleep(2))
    assert "שניות" in str(exc_info.value)


def test_watchdog_propagates_fn_exceptions():
    wd = Watchdog(timeout_sec=5.0)
    with pytest.raises(ValueError, match="boom"):
        wd.run(lambda: (_ for _ in ()).throw(ValueError("boom")))


def test_watchdog_custom_timeout_respected():
    wd = Watchdog(timeout_sec=0.2)
    start = time.monotonic()
    with pytest.raises(WatchdogTimeoutError):
        wd.run(lambda: time.sleep(10))
    elapsed = time.monotonic() - start
    assert elapsed < 1.0
