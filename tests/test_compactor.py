"""Unit tests for src/compactor.py — summarize logic (Anthropic client mocked)."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
from src.compactor import Compactor, _turns_to_text


def _make_mock_client(summary_text: str = "סיכום") -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.content = [MagicMock(text=summary_text)]
    response.usage.input_tokens = 10
    response.usage.output_tokens = 5
    client.messages.create.return_value = response
    return client


def _patched_compactor(summary_text: str = "סיכום") -> tuple[Compactor, MagicMock]:
    with patch("src.compactor.anthropic.Anthropic") as mock_cls, \
         patch("src.compactor.get_gatekeeper") as mock_gk:
        mock_gk.return_value = MagicMock()
        client = _make_mock_client(summary_text)
        mock_cls.return_value = client
        c = Compactor()
    return c, client


def test_summarize_empty_messages_returns_empty():
    with patch("src.compactor.anthropic.Anthropic"), patch("src.compactor.get_gatekeeper"):
        c = Compactor()
    assert c.summarize([]) == ""


def test_summarize_empty_messages_returns_prior_summary():
    with patch("src.compactor.anthropic.Anthropic"), patch("src.compactor.get_gatekeeper"):
        c = Compactor()
    assert c.summarize([], prior_summary="סיכום קיים") == "סיכום קיים"


def test_summarize_calls_api_and_returns_text():
    c, _ = _patched_compactor("הרפתקה מדהימה")
    messages = [
        {"role": "user", "content": "אני הולך ליער"},
        {"role": "assistant", "content": "אתה נכנס ליער האפל"},
    ]
    assert c.summarize(messages) == "הרפתקה מדהימה"


def test_summarize_fresh_prompt_used_when_no_prior_summary():
    c, client = _patched_compactor()
    c.summarize([{"role": "user", "content": "שלום"}])
    content = client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "סיכום קודם" not in content


def test_summarize_update_prompt_includes_prior_summary():
    c, client = _patched_compactor("סיכום מעודכן")
    c.summarize([{"role": "user", "content": "משהו חדש"}], prior_summary="סיכום קודם")
    content = client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "סיכום קודם" in content


def test_summarize_strips_whitespace_from_result():
    c, _ = _patched_compactor("  סיכום עם רווחים  ")
    result = c.summarize([{"role": "user", "content": "test"}])
    assert result == "סיכום עם רווחים"


def test_turns_to_text_labels_roles_correctly():
    messages = [
        {"role": "user", "content": "שלום"},
        {"role": "assistant", "content": "ברוכים הבאים"},
    ]
    text = _turns_to_text(messages)
    assert "שחקן: שלום" in text
    assert "DM: ברוכים הבאים" in text


def test_turns_to_text_truncates_long_content():
    long_content = "א" * 300
    messages = [{"role": "user", "content": long_content}]
    text = _turns_to_text(messages)
    assert len(text) < 300
