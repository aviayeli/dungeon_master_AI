from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Player:
    name: str
    character_class: str
    health: int
    max_health: int
    location: str
    inventory: list[str] = field(default_factory=list)


@dataclass
class GameState:
    player: Player
    history: list[dict[str, Any]] = field(default_factory=list)
    turn_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    context_summary: str = ""

    def save(self, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "player": {
                "name": self.player.name,
                "character_class": self.player.character_class,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "location": self.player.location,
                "inventory": self.player.inventory,
            },
            "history": self.history,
            "turn_count": self.turn_count,
            "created_at": self.created_at,
            "context_summary": self.context_summary,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, filepath: str | Path) -> GameState:
        path = Path(filepath)
        data = json.loads(path.read_text(encoding="utf-8"))
        player = Player(**data["player"])
        return cls(
            player=player,
            history=data.get("history", []),
            turn_count=data.get("turn_count", 0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            context_summary=data.get("context_summary", ""),
        )

    @classmethod
    def new_game(cls, name: str, character_class: str = "לוחם") -> GameState:
        from src.config import DEFAULT_MAX_HEALTH, DEFAULT_STARTING_LOCATION

        player = Player(
            name=name,
            character_class=character_class,
            health=DEFAULT_MAX_HEALTH,
            max_health=DEFAULT_MAX_HEALTH,
            location=DEFAULT_STARTING_LOCATION,
        )
        return cls(player=player)
