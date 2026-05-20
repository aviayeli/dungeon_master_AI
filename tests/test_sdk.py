"""Unit tests for src/sdk.py — DungeonMasterSDK (agent calls are mocked)."""
from __future__ import annotations
import threading
import pytest
from unittest.mock import MagicMock, patch

from src.sdk import DungeonMasterSDK


def _sdk_with_mock(tmp_path=None, **kwargs) -> DungeonMasterSDK:
    """Return an SDK instance with the Anthropic agent mocked out."""
    save = tmp_path / "save.json" if tmp_path else None
    with patch("src.sdk.DungeonMasterAgent"):
        sdk = DungeonMasterSDK(**({"save_path": save} if save else {}))
        sdk.new_game("גיבור", "לוחם")
    return sdk


# ---------------------------------------------------------------------------
# new_game / state access
# ---------------------------------------------------------------------------

def test_new_game_sets_player_name():
    with patch("src.sdk.DungeonMasterAgent"):
        sdk = DungeonMasterSDK()
        sdk.new_game("שמשון", "קשת")
    assert sdk._state.player.name == "שמשון"


def test_get_player_stats_keys():
    sdk = _sdk_with_mock()
    stats = sdk.get_player_stats()
    for key in ("name", "character_class", "health", "max_health", "location", "inventory", "turn_count"):
        assert key in stats


def test_get_player_stats_values():
    with patch("src.sdk.DungeonMasterAgent"):
        sdk = DungeonMasterSDK()
        sdk.new_game("בת-שבע", "כומר")
    stats = sdk.get_player_stats()
    assert stats["name"] == "בת-שבע"
    assert stats["character_class"] == "כומר"
    assert stats["health"] == stats["max_health"]
    assert isinstance(stats["inventory"], list)


def test_get_cost_stats_keys():
    sdk = _sdk_with_mock()
    cost = sdk.get_cost_stats()
    assert "total_cost_usd" in cost
    assert "input_tokens" in cost
    assert "output_tokens" in cost


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------

def test_save_and_load_via_sdk(tmp_path):
    save_file = tmp_path / "game.json"
    with patch("src.sdk.DungeonMasterAgent"):
        sdk = DungeonMasterSDK(save_path=save_file)
        sdk.new_game("ירדן", "גנב")
        sdk.save_game()
        sdk2 = DungeonMasterSDK(save_path=save_file)
        sdk2.load_game()
    assert sdk2.get_player_stats()["name"] == "ירדן"


def test_save_without_game_raises():
    with patch("src.sdk.DungeonMasterAgent"):
        sdk = DungeonMasterSDK()
    with pytest.raises(RuntimeError):
        sdk.save_game()


# ---------------------------------------------------------------------------
# is_thinking / send_message guards
# ---------------------------------------------------------------------------

def test_is_thinking_initially_false():
    sdk = _sdk_with_mock()
    assert sdk.is_thinking is False


def test_send_message_while_thinking_calls_on_error():
    sdk = _sdk_with_mock()
    sdk._thinking.set()
    errors: list[Exception] = []
    sdk.send_message("שלום", on_reply=lambda r: None, on_error=errors.append)
    assert len(errors) == 1
    assert "חושב" in str(errors[0])


def test_send_message_without_game_calls_on_error():
    with patch("src.sdk.DungeonMasterAgent"):
        sdk = DungeonMasterSDK()
    errors: list[Exception] = []
    sdk.send_message("שלום", on_reply=lambda r: None, on_error=errors.append)
    assert len(errors) == 1


def test_send_message_clears_thinking_on_completion():
    sdk = _sdk_with_mock()
    sdk._agent.send_message = MagicMock(return_value="תגובה")
    done = threading.Event()
    sdk.send_message("שלום", on_reply=lambda r: done.set(), on_error=lambda e: done.set())
    done.wait(timeout=5)
    assert sdk.is_thinking is False


def test_send_message_clears_thinking_on_error():
    sdk = _sdk_with_mock()
    sdk._agent.send_message = MagicMock(side_effect=RuntimeError("בעיה"))
    done = threading.Event()
    sdk.send_message("שלום", on_reply=lambda r: done.set(), on_error=lambda e: done.set())
    done.wait(timeout=5)
    assert sdk.is_thinking is False
