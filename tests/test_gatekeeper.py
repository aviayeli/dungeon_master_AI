"""Unit tests for src/gatekeeper.py — _Gatekeeper and BudgetExceededError."""
from __future__ import annotations
import pytest
from src.gatekeeper import _Gatekeeper, BudgetExceededError
from src.config import INPUT_COST_PER_MTOK, OUTPUT_COST_PER_MTOK, MAX_COST_USD


def _fresh() -> _Gatekeeper:
    """Return a clean Gatekeeper instance (bypasses the singleton)."""
    return _Gatekeeper()


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_initial_state():
    gk = _fresh()
    assert gk.total_input_tokens == 0
    assert gk.total_output_tokens == 0
    assert gk.total_cost_usd == 0.0


# ---------------------------------------------------------------------------
# record_usage
# ---------------------------------------------------------------------------

def test_record_usage_accumulates_tokens():
    gk = _fresh()
    gk.record_usage(100, 50)
    gk.record_usage(200, 75)
    assert gk.total_input_tokens == 300
    assert gk.total_output_tokens == 125


def test_cost_calculation_is_correct():
    gk = _fresh()
    gk.record_usage(1_000_000, 1_000_000)
    expected = INPUT_COST_PER_MTOK + OUTPUT_COST_PER_MTOK
    assert abs(gk.total_cost_usd - expected) < 1e-9


def test_cost_accumulates_across_calls():
    gk = _fresh()
    gk.record_usage(500_000, 0)
    gk.record_usage(500_000, 0)
    expected = INPUT_COST_PER_MTOK
    assert abs(gk.total_cost_usd - expected) < 1e-9


# ---------------------------------------------------------------------------
# check_budget
# ---------------------------------------------------------------------------

def test_check_budget_passes_under_limit():
    gk = _fresh()
    gk.record_usage(1, 1)
    gk.check_budget()  # must not raise


def test_check_budget_raises_at_limit():
    gk = _fresh()
    tokens_needed = int(MAX_COST_USD / INPUT_COST_PER_MTOK * 1_000_000) + 1
    gk.record_usage(tokens_needed, 0)
    with pytest.raises(BudgetExceededError):
        gk.check_budget()


def test_budget_error_message_contains_cost():
    gk = _fresh()
    tokens_needed = int(MAX_COST_USD / INPUT_COST_PER_MTOK * 1_000_000) + 1
    gk.record_usage(tokens_needed, 0)
    with pytest.raises(BudgetExceededError, match=r"\$"):
        gk.check_budget()


# ---------------------------------------------------------------------------
# reset
# ---------------------------------------------------------------------------

def test_reset_clears_all_fields():
    gk = _fresh()
    gk.record_usage(9999, 9999)
    gk.reset()
    assert gk.total_input_tokens == 0
    assert gk.total_output_tokens == 0
    assert gk.total_cost_usd == 0.0


def test_check_budget_passes_after_reset():
    gk = _fresh()
    tokens_needed = int(MAX_COST_USD / INPUT_COST_PER_MTOK * 1_000_000) + 1
    gk.record_usage(tokens_needed, 0)
    gk.reset()
    gk.check_budget()  # must not raise after reset
