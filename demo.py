"""
demo.py — offline GUI demo, no API key required.

Uses MockDungeonMasterSDK: scripted Hebrew replies, simulated thinking delay.
Run:  uv run demo.py
"""
from __future__ import annotations
import threading
import time

from src.gui_main import App
from src.state import GameState

DEMO_NAME = "גיבור הדמו"
DEMO_CLASS = "קוסם"
DEMO_INVENTORY = ["חרב אור", "מגן עץ", "כדור אש x3", "מפתח עתיק"]

_REPLIES = [
    "ברוך הבא לממלכת אלדוריה! אתה ניצב בכניסה ליער האפל. עצים עתיקים מקיפים אותך, "
    "וקול ינשוף נשמע מרחוק. מה ברצונך לעשות?",
    "אתה מתקדם לתוך היער. לפתע, אור מהבהב מאחורי שיח גדול מושך את תשומת לבך.",
    "מאחורי השיח מסתתר שועל זוהר קסום. הוא אומר: 'גיבור, המלך זקוק לעזרתך! לך לטירה!'",
    "אתה מגיע לשערי הטירה. השומר שואל: 'סיסמה?' מה תענה?",
    "הסיסמה נכונה! הדלת נפתחת. המלך מחייך ואומר: 'סוף סוף הגעת, גיבור!'",
]


class MockDungeonMasterSDK:
    def __init__(self) -> None:
        self._state: GameState | None = None
        self._thinking = threading.Event()
        self._idx = 0

    @property
    def is_thinking(self) -> bool:
        return self._thinking.is_set()

    def new_game(self, name: str, character_class: str = "לוחם") -> None:
        self._state = GameState.new_game(name, character_class)
        self._state.player.inventory = list(DEMO_INVENTORY)

    def load_game(self, filepath=None) -> None:
        raise FileNotFoundError("מצב דמו: אין קובץ שמירה")

    def save_game(self, filepath=None) -> None:
        pass

    def send_message(self, user_input, on_reply, on_error) -> None:  # noqa: ARG002
        if self._thinking.is_set():
            on_error(RuntimeError("הדאנג'ן מאסטר עדיין חושב."))
            return
        if self._state is None:
            on_error(RuntimeError("אין משחק פעיל."))
            return
        self._thinking.set()

        def _worker() -> None:
            try:
                time.sleep(1.5)
                reply = _REPLIES[self._idx % len(_REPLIES)]
                self._idx += 1
                self._state.turn_count += 1  # type: ignore[union-attr]
                on_reply(reply)
            finally:
                self._thinking.clear()

        threading.Thread(target=_worker, daemon=True).start()

    def get_player_stats(self) -> dict:
        if self._state is None:
            return {}
        p = self._state.player
        return {
            "name": p.name,
            "character_class": p.character_class,
            "health": p.health,
            "max_health": p.max_health,
            "location": p.location,
            "inventory": list(p.inventory),
            "turn_count": self._state.turn_count,
        }

    def get_cost_stats(self) -> dict:
        return {"total_cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0}


def main() -> None:
    sdk = MockDungeonMasterSDK()
    sdk.new_game(DEMO_NAME, DEMO_CLASS)
    App(sdk).mainloop()  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
