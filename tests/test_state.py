"""Unit tests for src/state.py — Player and GameState."""
from __future__ import annotations
import json
import pytest
from src.state import GameState, Player


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

def test_player_fields():
    p = Player(name="גיבור", character_class="לוחם", health=80,
               max_health=100, location="כפר")
    assert p.name == "גיבור"
    assert p.character_class == "לוחם"
    assert p.health == 80
    assert p.max_health == 100
    assert p.location == "כפר"
    assert p.inventory == []


def test_player_inventory_default_is_independent():
    p1 = Player("א", "לוחם", 100, 100, "עיר")
    p2 = Player("ב", "קוסם", 100, 100, "יער")
    p1.inventory.append("חרב")
    assert "חרב" not in p2.inventory


# ---------------------------------------------------------------------------
# GameState.new_game
# ---------------------------------------------------------------------------

def test_new_game_defaults():
    state = GameState.new_game("תמר")
    assert state.player.name == "תמר"
    assert state.player.character_class == "לוחם"
    assert state.player.health == state.player.max_health
    assert state.turn_count == 0
    assert state.history == []


def test_new_game_custom_class():
    state = GameState.new_game("אבנר", "קוסם")
    assert state.player.character_class == "קוסם"


# ---------------------------------------------------------------------------
# Save / Load
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_path):
    state = GameState.new_game("דינה")
    path = tmp_path / "save.json"
    state.save(path)
    assert path.exists()


def test_save_and_load_roundtrip(tmp_path):
    state = GameState.new_game("יונתן", "גנב")
    state.player.health = 55
    state.player.inventory.append("מפתח זהב")
    state.turn_count = 3
    state.history.append({"role": "user", "content": "שלום"})
    path = tmp_path / "save.json"
    state.save(path)

    loaded = GameState.load(path)
    assert loaded.player.name == "יונתן"
    assert loaded.player.character_class == "גנב"
    assert loaded.player.health == 55
    assert "מפתח זהב" in loaded.player.inventory
    assert loaded.turn_count == 3
    assert loaded.history[0]["content"] == "שלום"


def test_save_creates_parent_dirs(tmp_path):
    state = GameState.new_game("רינה")
    path = tmp_path / "deep" / "nested" / "save.json"
    state.save(path)
    assert path.exists()


def test_save_is_valid_json(tmp_path):
    state = GameState.new_game("עמוס")
    path = tmp_path / "save.json"
    state.save(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "player" in data
    assert "history" in data
    assert "turn_count" in data


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        GameState.load(tmp_path / "nonexistent.json")
