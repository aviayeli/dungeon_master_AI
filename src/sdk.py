from __future__ import annotations
import threading
from pathlib import Path
from typing import Callable

from src.agent import DungeonMasterAgent
from src.gatekeeper import get_gatekeeper
from src.state import GameState

DEFAULT_SAVE_PATH = Path("saves/game.json")


class DungeonMasterSDK:
    """Single entry-point for the GUI. Never expose Agent or GameState directly."""

    def __init__(self, save_path: str | Path = DEFAULT_SAVE_PATH) -> None:
        self._save_path = Path(save_path)
        self._state: GameState | None = None
        self._agent: DungeonMasterAgent | None = None
        self._thinking = threading.Event()  # set = inference in progress

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_thinking(self) -> bool:
        return self._thinking.is_set()

    @property
    def _active_state(self) -> GameState:
        if self._state is None:
            raise RuntimeError("אין משחק פעיל. קרא ל-new_game() או load_game() תחילה.")
        return self._state

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    def new_game(self, name: str, character_class: str = "לוחם") -> None:
        self._state = GameState.new_game(name, character_class)
        self._agent = DungeonMasterAgent(self._state)

    def load_game(self, filepath: str | Path | None = None) -> None:
        path = Path(filepath) if filepath else self._save_path
        self._state = GameState.load(path)
        self._agent = DungeonMasterAgent(self._state)

    def save_game(self, filepath: str | Path | None = None) -> None:
        path = Path(filepath) if filepath else self._save_path
        self._active_state.save(path)

    # ------------------------------------------------------------------
    # Non-blocking inference
    # ------------------------------------------------------------------

    def send_message(
        self,
        user_input: str,
        on_reply: Callable[[str], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        """Fire-and-forget: runs inference on a daemon thread, calls back when done."""
        if self._thinking.is_set():
            on_error(RuntimeError("הדאנג'ן מאסטר עדיין חושב. נסה שוב בעוד רגע."))
            return
        if self._agent is None:
            on_error(RuntimeError("אין משחק פעיל."))
            return

        self._thinking.set()

        def _worker() -> None:
            try:
                reply = self._agent.send_message(user_input)
                on_reply(reply)
            except Exception as exc:
                on_error(exc)
            finally:
                self._thinking.clear()

        threading.Thread(target=_worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Read-only state accessors for the GUI
    # ------------------------------------------------------------------

    def get_player_stats(self) -> dict:
        p = self._active_state.player
        return {
            "name": p.name,
            "character_class": p.character_class,
            "health": p.health,
            "max_health": p.max_health,
            "location": p.location,
            "inventory": list(p.inventory),
            "turn_count": self._active_state.turn_count,
        }

    def get_cost_stats(self) -> dict:
        gk = get_gatekeeper()
        return {
            "total_cost_usd": round(gk.total_cost_usd, 6),
            "input_tokens": gk.total_input_tokens,
            "output_tokens": gk.total_output_tokens,
        }
